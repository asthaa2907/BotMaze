from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid, os
from app.core.config import settings
from textblob import TextBlob

def detect_mood(message: str) -> str:
    """Detect mood based on message sentiment."""
    sentiment = TextBlob(message).sentiment.polarity
    if sentiment > 0.3:
        return "happy"
    elif sentiment < -0.3:
        return "sad"
    else:
        return "neutral"

# Initialize Qdrant client
qdrant = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key or None,
)

# Embedding model
embedder = SentenceTransformer(settings.embed_model)

COLLECTION_NAME = "botmaze_memory"

# Create collection if not exists
def init_memory():
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
        )
    print("✅ Qdrant memory initialized.")

def add_memory(user_id: str, text: str):
    vector = embedder.encode(text).tolist()
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"user_id": user_id, "text": text})
        ]
    )

def retrieve_memory(user_id: str, query: str, top_k=3):
    query_vector = embedder.encode(query).tolist()
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
        ),
    )
    return [hit.payload["text"] for hit in results]
