"""
Script to create a new Qdrant collection with correct dimensions
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
print(f"Current collection name: {QDRANT_COLLECTION_NAME}")

# Create new collection with correct dimensions (768 for Cohere embeddings)
new_collection_name = QDRANT_COLLECTION_NAME + "_new"
print(f"Creating new collection: {new_collection_name} with 768-dimensional vectors...")

try:
    client.create_collection(
        collection_name=new_collection_name,
        vectors_config=models.VectorParams(
            size=768,  # Cohere embed-multilingual-v2.0 returns 768-dimensional vectors
            distance=models.Distance.COSINE
        )
    )

    # Create payload index for efficient filtering
    client.create_payload_index(
        collection_name=new_collection_name,
        field_name="content_hash",
        field_schema=models.PayloadSchemaType.KEYWORD
    )

    print(f"Collection {new_collection_name} created successfully with 768-dimensional vectors")
    print("Now update your .env file to use this new collection name:")
    print(f"QDRANT_COLLECTION_NAME={new_collection_name}")

except Exception as e:
    print(f"Error creating collection: {str(e)}")
    print("This may be because the collection already exists.")

    # Check if the collection exists
    try:
        collection_info = client.get_collection(new_collection_name)
        print(f"Collection {new_collection_name} already exists with {collection_info.points_count} vectors")
        print(f"Vector size: {collection_info.config.params.vectors.size}")

        if collection_info.config.params.vectors.size != 768:
            print(f"WARNING: Existing collection has {collection_info.config.params.vectors.size} dimensions, but we need 768 for Cohere embeddings")
        else:
            print("Collection has the correct dimensions for Cohere embeddings.")

        print(f"Update your .env file to use this collection name:")
        print(f"QDRANT_COLLECTION_NAME={new_collection_name}")
    except:
        print(f"Collection {new_collection_name} does not exist and could not be created.")