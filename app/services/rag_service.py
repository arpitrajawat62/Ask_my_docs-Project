import os
import uuid
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langsmith import traceable

from app.config import get_settings

settings = get_settings()

# Langsmith tracing setup
os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com" 


# Singletons
_embeddings = None
_vectorestore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print(f"Loading embedding model...")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model
        )
        print("Embedding model loaded")
    return _embeddings

def get_vectorstore():
    global _vectorestore
    if _vectorestore is None:
        _vectorestore = Chroma(
            persist_directory=settings.chroma_persist_directory,
            embedding_function=get_embeddings(),
            collection_metadata={"hnsw:space": "cosine"}
        )
    return _vectorestore


# ingestion pipeline
@traceable(name="ingest_pipeline")
def ingest_pdf(file_bytes: bytes, filename: str) -> tuple[str, int]:

    doc_id = str(uuid.uuid4())
    
    # save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    
    # Load page
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages from '{filename}'")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")

    # Attach doc_id to every chunk
    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["filename"] = filename

    # store it in chromadb
    get_vectorstore().add_documents(chunks)
    print(f"Stored {len(chunks)} chunks in chromaDb")

    #cleanup temp files
    os.unlink(tmp_path)

    return doc_id, len(chunks)


    
# Retriever
@traceable(name="retrieve_chunks")
def retrieve_chunks(query: str, doc_id: str | None = None) -> list[dict]:

    search_kwargs = {"k": settings.top_k_chunks}
    if doc_id:
        search_kwargs["filter"] = {"doc_id": doc_id}

    retriever = get_vectorstore().as_retriever(search_kwargs=search_kwargs)
    docs = retriever.invoke(query)
    print(f"Retrived {len(docs)} chunks for query: '{query[:50]}'")

    return[
        {
            "chunk_id": i,
            "text": doc.page_content,
            "filename": doc.metadata.get("filename", "unknown"),
            "page": doc.metadata.get("page", 0),
        }
        for i, doc in enumerate(docs)
    ]