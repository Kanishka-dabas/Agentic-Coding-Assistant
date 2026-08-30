"""
Thin wrapper around the Qdrant client - centralizes connection details
and collection setup so ingestion.py and retriever.py don't duplicate
this logic.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance , VectorParams


COLLECTION_NAME = "codebase"
VECTOR_SIZE = 384

client = QdrantClient(host="localhost", port=6333)

def ensure_collection():
    """
    Creates the collection if it doesn't already exist. Safe to call
    every time the app starts - idempotent.
    """
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing :
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE , distance=Distance.COSINE)
        )
