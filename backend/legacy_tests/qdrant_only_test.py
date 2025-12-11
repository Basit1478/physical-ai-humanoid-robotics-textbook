import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Qdrant configuration using your provided credentials
QDRANT_URL = "https://912e150e-53c0-41d5-8bd5-62dc64dc85d0.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Bm4Y_u8wwMOjhS7YuFId-B-F4SRLio4gCkMXw5wO168"
COLLECTION_NAME = "hackathon-book"

def test_qdrant_connection():
    """Test Qdrant connection and basic operations"""
    print("Testing Qdrant connection...")
    print(f"Qdrant URL: {QDRANT_URL}")

    try:
        # Connect to Qdrant
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

        # Test connection
        info = client.get_collections()
        print("✅ Successfully connected to Qdrant!")
        print(f"Collections: {info}")

        # Test creating a collection
        collection_name = COLLECTION_NAME

        # Check if collection exists
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]

        if collection_name not in collection_names:
            print(f"Creating collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
            print("✅ Collection created successfully!")
        else:
            print(f"Collection {collection_name} already exists")

        # Test inserting a vector
        points = [
            PointStruct(
                id=1,
                vector=[0.1] * 1536,  # 1536-dimensional vector
                payload={"text": "This is a test point about AI and robotics"}
            ),
            PointStruct(
                id=2,
                vector=[0.2] * 1536,
                payload={"text": "This is another test point about physical AI"}
            )
        ]

        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print("✅ Successfully inserted test vectors!")

        # Test searching - using the correct API
        search_result = client.query(
            collection_name=collection_name,
            query_vector=[0.15] * 1536,
            limit=3
        )
        print(f"✅ Search successful! Found {len(search_result)} results")

        for result in search_result:
            print(f"  - Score: {result.score}, Payload: {result.payload}")

        # Clean up - delete test collection (optional)
        # Uncomment the next lines if you want to clean up
        # client.delete_collection(collection_name=collection_name)
        # print("✅ Test collection deleted!")

        return True

    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_qdrant_connection()