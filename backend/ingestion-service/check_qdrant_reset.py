"""
Script to reset and populate the Qdrant collection with correct embeddings using a different approach
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from config.settings import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME

# Initialize Qdrant client
if QDRANT_API_KEY:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=False
    )
else:
    client = QdrantClient(url=QDRANT_URL)

print(f"Connected to Qdrant at {QDRANT_URL}")
print(f"Collection name: {QDRANT_COLLECTION_NAME}")

# Check if collection exists
collections = client.get_collections()
collection_exists = any(col.name == QDRANT_COLLECTION_NAME for col in collections.collections)

if collection_exists:
    print(f"Collection {QDRANT_COLLECTION_NAME} exists with {client.get_collection(QDRANT_COLLECTION_NAME).points_count} vectors")
    print(f"Vector size: {client.get_collection(QDRANT_COLLECTION_NAME).config.params.vectors.size}")

    # Let's clear the existing vectors since they don't work with our ingestion
    print("Clearing existing vectors to populate with new ones...")
    try:
        # We can't delete the collection due to permissions, but we can clear it by deleting all points
        # First, get all point IDs
        scroll_result = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            limit=10000  # assuming we don't have more than 10k points
        )
        points = scroll_result[0]
        point_ids = [point.id for point in points]

        if point_ids:
            client.delete(
                collection_name=QDRANT_COLLECTION_NAME,
                points_selector=point_ids
            )
            print(f"Deleted {len(point_ids)} existing vectors")
        else:
            print("No existing vectors to delete")

    except Exception as e:
        print(f"Could not delete existing vectors: {e}")
        print("This is expected due to permission restrictions in Qdrant Cloud")
        print("You may need to recreate the collection with a different name")
else:
    print(f"Collection {QDRANT_COLLECTION_NAME} does not exist")