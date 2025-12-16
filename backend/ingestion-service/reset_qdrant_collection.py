"""
Script to delete the existing Qdrant collection and recreate it with correct dimensions
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
    print(f"Deleting existing collection: {QDRANT_COLLECTION_NAME}")
    client.delete_collection(QDRANT_COLLECTION_NAME)
    print("Collection deleted successfully")
else:
    print(f"Collection {QDRANT_COLLECTION_NAME} does not exist yet")

# Create new collection with correct dimensions (768 for Cohere embeddings)
print("Creating new collection with 768-dimensional vectors...")
client.create_collection(
    collection_name=QDRANT_COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size=768,  # Cohere embed-multilingual-v2.0 returns 768-dimensional vectors
        distance=models.Distance.COSINE
    )
)

# Create payload index for efficient filtering
client.create_payload_index(
    collection_name=QDRANT_COLLECTION_NAME,
    field_name="content_hash",
    field_schema=models.PayloadSchemaType.KEYWORD
)

print(f"Collection {QDRANT_COLLECTION_NAME} created successfully with 768-dimensional vectors")
print("You can now run the ingestion script again")