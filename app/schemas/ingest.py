from pydantic import BaseModel


class IngestResponse(BaseModel):

    doc_id: str
    filename: str
    chunk_count: int
    message: str = "Document ingested successfully"
