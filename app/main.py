from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ask, ingest, stream
from app.config import get_settings
from app.db.redis import close_redis, get_redis_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis_client()

    from app.services.rag_service import get_embeddings, get_vectorstore

    get_embeddings()
    get_vectorstore()

    yield

    await close_redis()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(ask.router)
app.include_router(stream.router)


@app.get("/")
async def health():
    return {"status": "running"}