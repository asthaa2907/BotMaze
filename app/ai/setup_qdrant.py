from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PayloadSchemaType
from app.core.config import settings

# Connect to Qdrant
client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key
)

collection_name = "botmaze_memory"

# Create or recreate collection
if not client.collection_exists(collection_name):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,  # vector size for MiniLM-L6-v2
            distance=Distance.COSINE
        )
    )
    print(f"✅ Created collection '{collection_name}' in Qdrant.")
else:
    print(f"⚡ Collection '{collection_name}' already exists.")

# Add index for filtering by user_id
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="user_id",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("✅ Added index on 'user_id' for memory retrieval.")
except Exception as e:
    print(f"⚠️ Index might already exist or failed: {e}")
