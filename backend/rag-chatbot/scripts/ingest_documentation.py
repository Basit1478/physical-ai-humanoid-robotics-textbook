#!/usr/bin/env python3
"""
Script to ingest all documentation content into the Qdrant collection for the RAG chatbot.
This script reads all the markdown files from the docs directory and adds them to the Qdrant collection.
"""

import os
import sys
import hashlib
from pathlib import Path

# Add the backend directory to the path so we can import the RAG agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rag_agent import RAGAgent
from config.settings import settings


def read_markdown_file(file_path: Path) -> str:
    """Read a markdown file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter if present (content between --- markers)
    lines = content.split('\n')
    if len(lines) > 0 and lines[0] == '---':
        # Find the second --- to skip frontmatter
        try:
            second_dash_idx = lines.index('---', 1)
            content = '\n'.join(lines[second_dash_idx + 1:])
        except ValueError:
            # If no second --- found, use the whole content
            pass

    return content.strip()


def chunk_text(text: str, max_chunk_size: int = 1000) -> list:
    """Split text into chunks of approximately max_chunk_size characters."""
    chunks = []
    paragraphs = text.split('\n\n')

    current_chunk = ""
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the chunk size
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            # Save the current chunk if it's not empty
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # Start a new chunk with the current paragraph
            current_chunk = paragraph
        else:
            # Add the paragraph to the current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # If any chunks are still too large, split them by sentences
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_chunk_size:
            final_chunks.append(chunk)
        else:
            # Split large chunk by sentences
            sentences = chunk.split('. ')
            temp_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence.endswith('.'):
                    sentence += '.'

                if len(temp_chunk) + len(sentence) <= max_chunk_size:
                    if temp_chunk:
                        temp_chunk += " " + sentence
                    else:
                        temp_chunk = sentence
                else:
                    if temp_chunk.strip():
                        final_chunks.append(temp_chunk.strip())
                    temp_chunk = sentence

            if temp_chunk.strip():
                final_chunks.append(temp_chunk.strip())

    return final_chunks


def get_document_url(file_path: Path) -> str:
    """Generate a URL-friendly identifier for the document."""
    # Convert to relative path from docs directory
    # The docs directory is at the project root level, not in backend
    docs_root = Path(__file__).parent.parent.parent.parent  # Go up to project root
    relative_path = file_path.relative_to(docs_root / "docs")
    # Convert to URL format
    url_path = str(relative_path).replace('\\', '/').replace('.md', '')
    return f"https://textbook-frontend-pl6r.onrender.com/docs/{url_path}"


async def main():
    """Main function to ingest all documentation content."""
    print("Starting documentation ingestion process...")

    # Initialize the RAG agent
    rag_agent = RAGAgent()

    # Get all markdown files from the docs directory
    # The docs directory is at the project root level, not in backend
    docs_dir = Path(__file__).parent.parent.parent.parent / "docs"

    if not docs_dir.exists():
        print(f"Docs directory does not exist: {docs_dir}")
        return

    markdown_files = list(docs_dir.rglob("*.md"))
    print(f"Found {len(markdown_files)} markdown files to process")

    total_chunks_ingested = 0
    total_documents_ingested = 0

    for i, file_path in enumerate(markdown_files, 1):
        print(f"Processing ({i}/{len(markdown_files)}): {file_path}")

        try:
            # Read the content of the markdown file
            content = read_markdown_file(file_path)

            if not content.strip():
                print(f"  Skipping empty file: {file_path}")
                continue

            # Get a title from the first line if it's a heading
            lines = content.split('\n')
            title = "Untitled Document"
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()  # Remove '# ' prefix
                    break
                elif line.startswith('title:'):
                    # Extract title from frontmatter if present
                    title = line[7:].strip().strip('"\'')
                    break

            # Generate document URL
            doc_url = get_document_url(file_path)

            # Create metadata
            metadata = {
                "source": "textbook",
                "file_path": str(file_path.relative_to(docs_dir)),
                "url": doc_url,
                "title": title,
                "document_type": "textbook_chapter"
            }

            # Chunk the content
            chunks = chunk_text(content, max_chunk_size=1000)
            print(f"  Split into {len(chunks)} chunks")

            # Ingest each chunk as a separate document
            for j, chunk in enumerate(chunks):
                chunk_title = f"{title} - Part {j+1}"
                chunk_url = f"{doc_url}#part-{j+1}"

                # Create specific metadata for this chunk
                chunk_metadata = metadata.copy()
                chunk_metadata["part"] = j + 1
                chunk_metadata["total_parts"] = len(chunks)

                try:
                    result = await rag_agent.ingest_single_document(
                        text=chunk,
                        title=chunk_title,
                        url=chunk_url,
                        metadata=chunk_metadata
                    )
                    print(f"    Ingested chunk {j+1}/{len(chunks)}")
                    total_chunks_ingested += 1
                except Exception as e:
                    print(f"    Error ingesting chunk {j+1}: {str(e)}")
                    continue

            total_documents_ingested += 1
            print(f"  Successfully processed: {title}")

        except Exception as e:
            print(f"  Error processing {file_path}: {str(e)}")
            continue

    print(f"\nIngestion completed!")
    print(f"Documents processed: {total_documents_ingested}")
    print(f"Chunks ingested: {total_chunks_ingested}")

    # Print collection stats
    try:
        service_info = rag_agent.get_service_info()
        collection_info = service_info.get('collection_info', {})
        print(f"Current collection stats: {collection_info}")
    except Exception as e:
        print(f"Could not retrieve collection stats: {str(e)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())