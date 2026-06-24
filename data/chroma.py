from functools import lru_cache

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings

settings = get_settings()



@lru_cache
def get_embedder() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model
    )


@lru_cache
def get_vector_store() -> Chroma:
    return Chroma(
        persist_directory=settings.chroma_persist_directory,
        embedding_function=get_embedder(),
    )