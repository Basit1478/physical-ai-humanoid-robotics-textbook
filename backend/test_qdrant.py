import os
from config import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def test_qdrant_connection():
    """Test Qdrant connection and basic operations"""
    print("Testing Qdrant connection...")
    print(f"Qdrant URL: {settings.qdrant_url}")

    try:
        # Try to connect to Qdrant
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        # Test connection
        info = client.get_collections()
        print("✅ Successfully connected to Qdrant!")
        print(f"Collections: {info}")

        # Test creating a collection
        collection_name = "test_collection"

        # Check if collection exists
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if collection_name not in collection_names:
            print(f"Creating test collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            print("✅ Collection created successfully!")
        else:
            print(f"Collection {collection_name} already exists")

        # Test inserting a vector
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(
                id=1,
                vector=[0.1] * 1536,  # 1536-dimensional vector
                payload={"text": "This is a test point"}
            )
        ]

        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print("✅ Successfully inserted test vector!")

        # Test searching
        search_result = client.search(
            collection_name=collection_name,
            query_vector=[0.1] * 1536,
            limit=3
        )
        print(f"✅ Search successful! Found {len(search_result)} results")

        # Clean up - delete test collection
        client.delete_collection(collection_name=collection_name)
        print("✅ Test collection deleted!")

        return True

    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        return False

if __name__ == "__main__":
    test_qdrant_connection()