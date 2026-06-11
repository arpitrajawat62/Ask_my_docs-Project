from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api import ingest, ask, stream
from app.db.chroma import init_qdrant
from app.db.redis import get_redis_client


settings = get_settings()



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_qdrant()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)


@app.get("/")
async def health():
    return {"status": "running"}