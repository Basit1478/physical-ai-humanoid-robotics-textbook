"""
Main ingestion service that orchestrates crawling, chunking, embedding, and storage
"""
import asyncio
import logging
import time
import hashlib
from typing import List, Dict
from datetime import datetime

from .crawler import AsyncCrawler, ContentProcessor
from .embedding_service import EmbeddingService
from .qdrant_service import QdrantStorage
from config.settings import (
    CHUNK_SIZE_MIN, CHUNK_SIZE_MAX, CHUNK_OVERLAP,
    RETRY_ATTEMPTS, RETRY_DELAY
)


class IngestionService:
    def __init__(self):
        self.crawler = AsyncCrawler()
        self.content_processor = ContentProcessor()
        self.embedding_service = EmbeddingService()
        self.qdrant_storage = QdrantStorage()

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Stats tracking
        self.stats = {
            'start_time': None,
            'end_time': None,
            'pages_crawled': 0,
            'chunks_processed': 0,
            'embeddings_generated': 0,
            'vectors_stored': 0,
            'errors': []
        }

    async def run_ingestion_pipeline(self, base_url: str = None) -> Dict:
        """
        Run the complete ingestion pipeline: crawl -> extract -> chunk -> embed -> store
        """
        self.stats['start_time'] = time.time()
        self.logger.info("Starting ingestion pipeline...")

        try:
            # Update base URL if provided
            if base_url:
                self.crawler.base_url = base_url

            # Step 1: Crawl the website
            self.logger.info("Step 1: Crawling website...")
            crawled_pages = await self.crawl_website()
            self.stats['pages_crawled'] = len(crawled_pages)

            if not crawled_pages:
                self.logger.warning("No pages were crawled successfully")
                return self._get_summary_report()

            # Step 2: Process content (chunking)
            self.logger.info("Step 2: Processing and chunking content...")
            chunks = self.process_content(crawled_pages)
            self.stats['chunks_processed'] = len(chunks)

            if not chunks:
                self.logger.warning("No content chunks were created")
                return self._get_summary_report()

            # Step 3: Generate embeddings
            self.logger.info("Step 3: Generating embeddings...")
            chunks_with_embeddings = await self.generate_embeddings(chunks)
            self.stats['embeddings_generated'] = len([c for c in chunks_with_embeddings if 'embedding' in c])

            # Step 4: Initialize Qdrant collection
            self.logger.info("Step 4: Initializing Qdrant collection...")
            embedding_dimensions = len(chunks_with_embeddings[0]['embedding']) if chunks_with_embeddings and 'embedding' in chunks_with_embeddings[0] else 1024
            self.qdrant_storage.initialize_collection(vector_size=embedding_dimensions)

            # Step 5: Store vectors in Qdrant
            self.logger.info("Step 5: Storing vectors in Qdrant...")
            await self.store_vectors(chunks_with_embeddings)
            self.stats['vectors_stored'] = len([c for c in chunks_with_embeddings if 'embedding' in c])

            self.logger.info("Ingestion pipeline completed successfully!")

        except Exception as e:
            error_msg = f"Error in ingestion pipeline: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)

        finally:
            self.stats['end_time'] = time.time()
            summary = self._get_summary_report()
            self.logger.info(f"Pipeline completed. {summary}")
            await self.crawler.close()  # Close the crawler's HTTP client

        return self._get_summary_report()

    async def crawl_website(self) -> List[Dict]:
        """
        Crawl the website and return the crawled content.
        """
        try:
            crawled_pages = await self.crawler.crawl_site()
            return crawled_pages
        except Exception as e:
            error_msg = f"Error during crawling: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return []

    def process_content(self, crawled_pages: List[Dict]) -> List[Dict]:
        """
        Process crawled content by chunking it.
        """
        try:
            chunks = self.content_processor.process_content(
                crawled_pages,
                min_tokens=CHUNK_SIZE_MIN,
                max_tokens=CHUNK_SIZE_MAX,
                overlap=CHUNK_OVERLAP
            )
            return chunks
        except Exception as e:
            error_msg = f"Error during content processing: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return []

    async def generate_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for the content chunks.
        """
        if not chunks:
            return []

        try:
            # Extract texts for embedding
            texts = [chunk['text'] for chunk in chunks]

            # Generate embeddings
            embeddings = self.embedding_service.generate_embeddings(texts)

            # Combine chunks with their embeddings
            chunks_with_embeddings = []
            for i, chunk in enumerate(chunks):
                if i < len(embeddings):
                    chunk_copy = chunk.copy()
                    chunk_copy['embedding'] = embeddings[i]
                    # Add content hash for idempotent storage
                    content_hash = hashlib.md5(chunk['text'].encode()).hexdigest()
                    chunk_copy['content_hash'] = content_hash
                    chunks_with_embeddings.append(chunk_copy)
                else:
                    self.logger.error(f"No embedding generated for chunk {i}")

            return chunks_with_embeddings

        except Exception as e:
            error_msg = f"Error during embedding generation: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return []

    async def store_vectors(self, chunks_with_embeddings: List[Dict]):
        """
        Store the embedded chunks in Qdrant.
        """
        if not chunks_with_embeddings:
            self.logger.warning("No chunks with embeddings to store")
            return

        try:
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
            self.qdrant_storage.idempotent_upsert(vectors_data)

        except Exception as e:
            error_msg = f"Error during vector storage: {str(e)}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    def _get_summary_report(self) -> Dict:
        """
        Generate a summary report of the ingestion process.
        """
        duration = (self.stats['end_time'] - self.stats['start_time']) if self.stats['start_time'] and self.stats['end_time'] else 0

        report = {
            'status': 'completed_with_errors' if self.stats['errors'] else 'completed_successfully',
            'summary': {
                'pages_crawled': self.stats['pages_crawled'],
                'chunks_processed': self.stats['chunks_processed'],
                'embeddings_generated': self.stats['embeddings_generated'],
                'vectors_stored': self.stats['vectors_stored'],
                'duration_seconds': round(duration, 2),
                'start_time': datetime.fromtimestamp(self.stats['start_time']).isoformat() if self.stats['start_time'] else None,
                'end_time': datetime.fromtimestamp(self.stats['end_time']).isoformat() if self.stats['end_time'] else None
            },
            'errors': self.stats['errors'],
            'collection_info': self.qdrant_storage.get_collection_info() if self.stats['vectors_stored'] > 0 else {}
        }

        return report

    async def run(self, base_url: str = None):
        """
        Convenience method to run the ingestion and print a formatted report.
        """
        report = await self.run_ingestion_pipeline(base_url)

        print("\n" + "="*60)
        print("INGESTION PIPELINE SUMMARY")
        print("="*60)
        print(f"Status: {report['status']}")
        print(f"Pages Crawled: {report['summary']['pages_crawled']}")
        print(f"Chunks Processed: {report['summary']['chunks_processed']}")
        print(f"Embeddings Generated: {report['summary']['embeddings_generated']}")
        print(f"Vectors Stored: {report['summary']['vectors_stored']}")
        print(f"Duration: {report['summary']['duration_seconds']} seconds")

        if report['errors']:
            print(f"\nErrors ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"  - {error}")

        if report['collection_info']:
            print(f"\nCollection Info:")
            print(f"  Vector Count: {report['collection_info'].get('vector_count', 'N/A')}")

        print("="*60)

        return report


# Main execution function
async def main():
    """
    Main function to run the ingestion service.
    """
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Get base URL from environment or use default
    base_url = os.getenv("DOCUSAURUS_BASE_URL")

    if not base_url:
        print("Please set DOCUSAURUS_BASE_URL environment variable")
        return

    # Create and run ingestion service
    ingestion_service = IngestionService()
    report = await ingestion_service.run(base_url)

    return report


if __name__ == "__main__":
    # Run the ingestion service
    asyncio.run(main())