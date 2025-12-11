import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.qdrant_mcp_service import qdrant_mcp_service

def test_qdrant_connection():
    """Test Qdrant connection and basic operations"""
    print("Testing Qdrant connection...")

    try:
        # Test connection
        info = qdrant_mcp_service.client.get_collections()
        print("✅ Successfully connected to Qdrant!")
        print(f"Collections: {info}")

        # Test creating a collection
        collection_name = "test_collection"

        # Check if collection exists
        collections = qdrant_mcp_service.client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if collection_name not in collection_names:
            print(f"Creating test collection: {collection_name}")
            from qdrant_client.models import VectorParams, Distance
            qdrant_mcp_service.client.create_collection(
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

        qdrant_mcp_service.client.upsert(
            collection_name=collection_name,
            points=points
        )
        print("✅ Successfully inserted test vector!")

        # Test searching
        search_result = qdrant_mcp_service.client.search(
            collection_name=collection_name,
            query_vector=[0.1] * 1536,
            limit=3
        )
        print(f"✅ Search successful! Found {len(search_result)} results")

        # Clean up - delete test collection
        qdrant_mcp_service.client.delete_collection(collection_name=collection_name)
        print("✅ Test collection deleted!")

        return True

    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        return False

if __name__ == "__main__":
    test_qdrant_connection()