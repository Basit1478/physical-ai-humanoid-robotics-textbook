"""
Script to ingest local Markdown documents into Qdrant for the RAG system
"""
import asyncio
import os
import hashlib
from pathlib import Path
from typing import List, Dict
import logging
import time
from datetime import datetime

from src.embedding_service import EmbeddingService
from src.qdrant_service import QdrantStorage
from utils.tokenization import chunk_text, clean_text
from config.settings import (
    CHUNK_SIZE_MIN, CHUNK_SIZE_MAX, CHUNK_OVERLAP
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_markdown_files(docs_dir: str) -> List[Dict]:
    """
    Read all markdown files from the docs directory and extract content.

    Args:
        docs_dir: Path to the docs directory containing markdown files

    Returns:
        List of dictionaries with file content and metadata
    """
    docs_path = Path(docs_dir)
    markdown_files = list(docs_path.rglob("*.md"))

    documents = []

    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from the first heading in the file
            title = extract_title_from_content(content)

            # Create a relative URL-like path for the document
            relative_path = file_path.relative_to(docs_path)
            url_path = f"/docs/{relative_path.as_posix()}"

            # Clean the content by removing frontmatter if present
            cleaned_content = remove_frontmatter(content)

            document = {
                'url': url_path,
                'title': title,
                'content': cleaned_content,
                'file_path': str(file_path),
                'content_hash': hashlib.md5(cleaned_content.encode()).hexdigest(),
                'fetched_at': time.time()
            }

            documents.append(document)
            logger.info(f"Processed file: {file_path}")

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")

    return documents


def extract_title_from_content(content: str) -> str:
    """
    Extract title from markdown content (first H1 heading).

    Args:
        content: Raw markdown content

    Returns:
        Extracted title or empty string if not found
    """
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            title = line.strip()[2:].strip()  # Remove '# ' prefix
            return title

    # If no H1 found, try to get from the first non-empty line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('---'):
            # Take the first sentence or first 50 characters
            if '.' in stripped:
                title = stripped.split('.')[0]
            else:
                title = stripped[:50]
            return title.strip()

    return "Untitled Document"


def remove_frontmatter(content: str) -> str:
    """
    Remove YAML frontmatter from markdown content if present.

    Args:
        content: Raw markdown content

    Returns:
        Content without frontmatter
    """
    lines = content.split('\n')
    if len(lines) < 2:
        return content

    # Check if the file starts with frontmatter (--- at beginning)
    if lines[0].strip() == '---':
        # Find the closing ---
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                # Return content after the closing ---
                return '\n'.join(lines[i+1:]).strip()

    return content


def process_documents(documents: List[Dict]) -> List[Dict]:
    """
    Process documents by chunking them into smaller pieces.

    Args:
        documents: List of document dictionaries

    Returns:
        List of processed chunks
    """
    processed_chunks = []

    for doc in documents:
        content = doc['content']

        # Chunk the content
        chunks = chunk_text(content, CHUNK_SIZE_MIN, CHUNK_SIZE_MAX, CHUNK_OVERLAP)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['content_hash']}_chunk_{i}"

            processed_chunk = {
                'chunk_id': chunk_id,
                'url': doc['url'],
                'title': doc['title'],
                'text': chunk['text'],
                'token_count': chunk['token_count'],
                'position': i,
                'page_hash': doc['content_hash'],
                'source_metadata': {
                    'original_url': doc['url'],
                    'title': doc['title'],
                    'position_in_page': i,
                    'total_chunks_in_page': len(chunks),
                    'file_path': doc['file_path']
                }
            }

            processed_chunks.append(processed_chunk)

    logger.info(f"Processed {len(documents)} documents into {len(processed_chunks)} chunks")
    return processed_chunks


async def ingest_documents_to_qdrant():
    """
    Main function to ingest local documents into Qdrant.
    """
    logger.info("Starting ingestion of local documents to Qdrant...")

    start_time = time.time()

    try:
        # Read markdown files from docs directory
        logger.info("Reading markdown files from docs directory...")
        documents = read_markdown_files("../../docs")  # Relative to backend/ingestion-service/

        if not documents:
            logger.warning("No documents found to process")
            return {
                'status': 'no_documents_found',
                'summary': {
                    'documents_processed': 0,
                    'chunks_created': 0,
                    'embeddings_generated': 0,
                    'vectors_stored': 0,
                    'duration_seconds': 0
                }
            }

        # Process documents (chunking)
        logger.info("Processing and chunking documents...")
        chunks = process_documents(documents)

        if not chunks:
            logger.warning("No content chunks were created")
            return

        # Initialize embedding service
        logger.info("Initializing embedding service...")
        embedding_service = EmbeddingService()

        # Get the correct embedding dimensions from the model
        logger.info("Getting embedding dimensions from model...")
        embedding_dimensions = embedding_service._get_embedding_dimensions()
        logger.info(f"Embedding dimensions: {embedding_dimensions}")

        # Initialize Qdrant storage
        logger.info("Initializing Qdrant storage...")
        qdrant_storage = QdrantStorage()

        # Initialize collection with proper dimensions BEFORE generating embeddings
        qdrant_storage.initialize_collection(vector_size=embedding_dimensions)

        # Generate embeddings
        logger.info("Generating embeddings...")
        texts = [chunk['text'] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(texts)

        # Combine chunks with embeddings, ensuring 1536-dimensional vectors for compatibility
        chunks_with_embeddings = []
        for i, chunk in enumerate(chunks):
            if i < len(embeddings):
                chunk_copy = chunk.copy()

                # Get the original embedding (likely 768 dimensions from Cohere)
                original_embedding = embeddings[i]

                # Extend to 1536 dimensions for compatibility with existing Qdrant collection
                # This is a workaround to match the expected 1536 dimensions
                if len(original_embedding) == 768:
                    # Duplicate the embedding to create 1536 dimensions
                    extended_embedding = original_embedding + original_embedding
                elif len(original_embedding) == 1536:
                    # Already correct size
                    extended_embedding = original_embedding
                else:
                    # For other sizes, pad or truncate as needed
                    target_size = 1536
                    if len(original_embedding) < target_size:
                        # Pad with zeros
                        extended_embedding = original_embedding + [0.0] * (target_size - len(original_embedding))
                    else:
                        # Truncate
                        extended_embedding = original_embedding[:target_size]

                chunk_copy['embedding'] = extended_embedding
                # Add content hash for idempotent storage
                content_hash = hashlib.md5(chunk['text'].encode()).hexdigest()
                chunk_copy['content_hash'] = content_hash
                chunks_with_embeddings.append(chunk_copy)
            else:
                logger.error(f"No embedding generated for chunk {i}")

        if not chunks_with_embeddings:
            logger.error("No chunks with embeddings to store")
            return

        # Prepare data for Qdrant
        vectors_data = []
        for chunk in chunks_with_embeddings:
            if 'embedding' in chunk:
                # Create payload with metadata
                payload = {
                    'url': chunk['url'],
                    'title': chunk['title'],
                    'text': chunk['text'],
                    'position': chunk['position'],
                    'token_count': chunk.get('token_count', len(chunk['text'].split())),
                    'content_hash': chunk['content_hash'],
                    'source_metadata': chunk.get('source_metadata', {}),
                    'created_at': datetime.utcnow().isoformat()
                }

                # Use content hash as the ID for idempotent storage
                vector_id = chunk['content_hash']

                vectors_data.append({
                    'id': vector_id,
                    'vector': chunk['embedding'],
                    'payload': payload
                })

        # Perform idempotent upsert to avoid duplicates
        logger.info(f"Storing {len(vectors_data)} vectors in Qdrant...")
        qdrant_storage.idempotent_upsert(vectors_data)

        duration = time.time() - start_time

        logger.info(f"Ingestion completed successfully!")
        logger.info(f"Processed {len(documents)} documents")
        logger.info(f"Created {len(chunks)} chunks")
        logger.info(f"Generated {len(chunks_with_embeddings)} embeddings")
        logger.info(f"Stored {len(vectors_data)} vectors in Qdrant")
        logger.info(f"Total duration: {duration:.2f} seconds")

        # Print collection info
        collection_info = qdrant_storage.get_collection_info()
        if collection_info:
            logger.info(f"Collection vector count: {collection_info.get('vector_count', 'N/A')}")

        return {
            'status': 'completed_successfully',
            'summary': {
                'documents_processed': len(documents),
                'chunks_created': len(chunks),
                'embeddings_generated': len(chunks_with_embeddings),
                'vectors_stored': len(vectors_data),
                'duration_seconds': round(duration, 2)
            },
            'collection_info': collection_info
        }

    except Exception as e:
        error_msg = f"Error during document ingestion: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()

        return {
            'status': 'error',
            'error': error_msg,
            'summary': {}
        }


if __name__ == "__main__":
    # Run the ingestion
    result = asyncio.run(ingest_documents_to_qdrant())

    print("\n" + "="*60)
    print("DOCUMENT INGESTION SUMMARY")
    print("="*60)
    print(f"Status: {result['status']}")

    if 'summary' in result:
        summary = result['summary']
        print(f"Documents Processed: {summary.get('documents_processed', 0)}")
        print(f"Chunks Created: {summary.get('chunks_created', 0)}")
        print(f"Embeddings Generated: {summary.get('embeddings_generated', 0)}")
        print(f"Vectors Stored: {summary.get('vectors_stored', 0)}")
        print(f"Duration: {summary.get('duration_seconds', 0)} seconds")

    if 'collection_info' in result and result['collection_info']:
        print(f"\nCollection Info:")
        print(f"  Vector Count: {result['collection_info'].get('vector_count', 'N/A')}")

    if 'error' in result:
        print(f"\nError: {result['error']}")

    print("="*60)