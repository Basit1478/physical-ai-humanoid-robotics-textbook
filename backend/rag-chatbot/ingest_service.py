#!/usr/bin/env python3
"""
Ingestion service for the RAG chatbot system.
This service handles the ingestion of textbook content into the Qdrant collection.
"""

import os
import sys
import hashlib
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add the backend directory to the path so we can import the RAG agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from utils.qdrant_retriever import QdrantRetriever
from src.rag_agent import RAGAgent


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
    docs_root = Path(__file__).parent.parent.parent  # Go up to project root
    relative_path = file_path.relative_to(docs_root / "docs")
    # Convert to URL format
    url_path = str(relative_path).replace('\\', '/').replace('.md', '')
    return f"https://basit1478.github.io/docs/{url_path}"


def generate_embeddings_batch(texts: List[str], batch_size: int = 96) -> List[List[float]]:  # Cohere max is 96
    """
    Generate embeddings for a batch of texts using Cohere.
    """
    import cohere
    import time

    all_embeddings = []
    cohere_client = cohere.Client(settings.COHERE_API_KEY)

    # Process in batches to respect API limits
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        try:
            response = cohere_client.embed(
                texts=batch,
                model=settings.COHERE_MODEL,
                input_type="search_document",  # Use search_document for ingestion
                embedding_types=["float"]
            )

            # Extract embeddings - for v3 models with embedding_types, the result is nested
            batch_embeddings = response.embeddings.float

            # Ensure each embedding is exactly 768 dimensions
            for embedding in batch_embeddings:
                while len(embedding) < 768:
                    embedding.append(0.0)
                embedding = embedding[:768]
                all_embeddings.append(embedding)

            # Add a small delay to respect rate limits
            time.sleep(1.5)

        except Exception as e:
            print(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
            # Fallback: generate placeholder embeddings for the entire batch
            for text in batch:
                placeholder_embedding = create_placeholder_embedding_768(text)
                all_embeddings.append(placeholder_embedding)

    return all_embeddings


def create_placeholder_embedding_768(text: str) -> List[float]:
    """
    Create a placeholder embedding when Cohere fails.
    """
    import hashlib

    # Create a hash of the text
    hash_obj = hashlib.sha256(text.encode())
    hex_dig = hash_obj.hexdigest()

    # Convert hex to a list of floats
    embedding = []
    for i in range(0, len(hex_dig), 2):
        if i + 1 < len(hex_dig):
            val = int(hex_dig[i:i+2], 16) / 255.0  # Normalize to 0-1
            embedding.append(val)

    # Pad or truncate to exactly 768 dimensions
    while len(embedding) < 768:
        embedding.append(0.0)
    embedding = embedding[:768]

    return embedding


async def main():
    """Main function to ingest all textbook documentation content."""
    print("Starting textbook content ingestion process...")

    # Get all markdown files from the docs directory
    docs_dir = Path(__file__).parent.parent / "docs"

    if not docs_dir.exists():
        print(f"Docs directory does not exist: {docs_dir}")
        return

    # Find all markdown files including in subdirectories
    markdown_files = list(docs_dir.rglob("*.md"))
    print(f"Found {len(markdown_files)} markdown files to process")

    # Collect all chunks to be ingested
    all_chunks_data = []

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

            # Prepare chunk data for batch processing
            for j, chunk in enumerate(chunks):
                chunk_title = f"{title} - Part {j+1}"
                chunk_url = f"{doc_url}#part-{j+1}"

                # Create specific metadata for this chunk
                chunk_metadata = metadata.copy()
                chunk_metadata["part"] = j + 1
                chunk_metadata["total_parts"] = len(chunks)

                all_chunks_data.append({
                    'text': chunk,
                    'title': chunk_title,
                    'url': chunk_url,
                    'metadata': chunk_metadata,
                    'file_path': file_path,
                    'chunk_index': j
                })

        except Exception as e:
            print(f"  Error processing {file_path}: {str(e)}")
            continue

    print(f"\nCollected {len(all_chunks_data)} total chunks for ingestion")

    # Extract all texts for batch embedding
    all_texts = [chunk_data['text'] for chunk_data in all_chunks_data]

    # Generate embeddings in batches
    print("Generating embeddings in batches...")
    embeddings = generate_embeddings_batch(all_texts)

    # Initialize QdrantRetriever to store the vectors
    print("Initializing Qdrant client...")
    qdrant_retriever = QdrantRetriever()

    # Store all vectors in Qdrant
    print("Storing vectors in Qdrant...")
    success_count = 0
    for i, chunk_data in enumerate(all_chunks_data):
        try:
            embedding = embeddings[i]

            # Create content hash for idempotent storage
            content_hash = hashlib.md5(chunk_data['text'].encode()).hexdigest()

            # Prepare payload with metadata
            payload = {
                'url': chunk_data['url'],
                'title': chunk_data['title'],
                'text': chunk_data['text'],
                'position': 0,  # Single chunk, position 0
                'token_count': len(chunk_data['text'].split()),
                'content_hash': content_hash,
                'source_metadata': chunk_data['metadata'],
                'created_at': datetime.now().isoformat()
            }

            # Store the vector in Qdrant
            success = qdrant_retriever.store_single_vector(
                vector_id=content_hash,
                vector=embedding,
                payload=payload
            )

            if success:
                success_count += 1
                if success_count % 10 == 0:  # Print progress every 10 successful uploads
                    print(f"  Stored {success_count}/{len(all_chunks_data)} chunks...")
            else:
                print(f"  Failed to store chunk {i+1}")

        except Exception as e:
            print(f"  Error storing chunk {i+1}: {str(e)}")
            continue

    print(f"\nIngestion completed!")
    print(f"Chunks processed: {len(all_chunks_data)}")
    print(f"Chunks successfully stored: {success_count}")

    # Print collection stats
    try:
        service_info = RAGAgent().get_service_info()
        collection_info = service_info.get('collection_info', {})
        print(f"Current collection stats: {collection_info}")
    except Exception as e:
        print(f"Could not retrieve collection stats: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())