from pydantic import BaseModel
from typing import List



class SourceChunk(BaseModel):
    chunk_id: int
    text: str
    


class AskRequest(BaseModel):
    query: str
    doc_id: str | None = None
    session_id: str = "default"


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    session_id: str


class StreamRequest(BaseModel):
    query: str
    doc_id: str | None = None
    session_id: str = "default"

