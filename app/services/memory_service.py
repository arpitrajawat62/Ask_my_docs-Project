import json
import os
from langsmith import traceable

from app.db.redis import get_redis_client
from app.config import get_settings


settings = get_settings()


# Langsmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key

_TTL = 60 * 60 * 24   # 24 hours


# save
@traceable(name="save")
async def save_turn(session_id: str, question: str, answer: str) -> None:
    
    redis = await get_redis_client()
    key = f"chat:{session_id}"

    await redis.rpush(key, json.dumps({"role": "user", "content": question}))
    await redis.rpush(key, json.dumps({"role": "assistant", "content": answer}))
    await redis.expire(key, _TTL)


# Load  history
@traceable(name="load_history")
async def load_history(session_id: str) -> list[dict]:

    redis = await get_redis_client()
    key = f"chat:{session_id}"

    all_messages = await redis.lrange(key, 0, -1)
    messages = [json.loads(m) for m in all_messages]

    limit = settings.chat_history_limit
    return messages[-(limit * 2):]



# full history
@traceable(name="load_full_history")
async def get_full_history(session_id: str) -> list[dict]:

    redis = await get_redis_client()
    all_messages = await redis.lrange(f"chat:{session_id}", 0, -1)
    return [json.loads(m) for m in all_messages]



# delete history
@traceable(name="clear_history")
async def delete_history(session_id: str) -> int:

    redis = await get_redis_client()
    key = f"chat:{session_id}"
    count = await redis.llen(key)
    await redis.delete(key)
    return count

