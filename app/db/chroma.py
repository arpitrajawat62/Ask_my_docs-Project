import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import get_settings


settings = get_settings()

_client = None


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
        )
    return _client


def get_collection():

    client = get_chroma_client()
    return client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"},
    )