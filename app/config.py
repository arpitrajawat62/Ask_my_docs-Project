from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):

    # App
    app_name: str = "Ask-My-Docs API"    
    
    # LLM 
    gemini_api_key: str

    # Vector DB
    chroma_persist_directory: str = "./data/chroma"


    # Embedding Model
    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )


    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 100

    # Retrieval
    top_k_chunks: int = 5
    chat_history_limit: int = 5


    # Redis
    redis_url: str = "redis://localhost:6379"

    # LangSmith
    langchain_api_key: str = ""
    langchain_tracing_v2: bool = True
    langchain_project: str = "ask-my-docs"


    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
