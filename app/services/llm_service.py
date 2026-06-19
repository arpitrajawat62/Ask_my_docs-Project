import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langsmith import traceable

from app.config import get_settings

settings = get_settings()


# LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"


# Singleton 
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=settings.gemini_api_key,
        )
        print("Gemini model loaded")
    return _llm


# build msg
def build_message(history: list[dict], context: str, question: str) -> list:

    messages = []
    
    # introduction
    messages.append(SystemMessage(content=(   
        "You are a helpful assistant that answers questions "
        "strictly based on the document context provided.\n"
        "If the answer is not in the context, say: "
        "'I couldn't find that in the document.'"
    )))
    
    # Past conversation history
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    # Current question with context
    messages.append(HumanMessage(content=(
        f"Context from documents:\n\n{context}"
        f"\n\nQuestion: {question}"
    )))
    return messages

# format chunks into readable context string
def format_context(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        parts.append(
            f"[Page {chunk['page']} | {chunk['filename']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)


# generate ans
@traceable(name="generate_answer")
def generate_answer(chunks: list[dict], question: str, history: list[dict]) -> str:
     
    llm = get_llm()
    context = format_context(chunks)
    messages = build_message(history, context, question)
    response = llm.invoke(messages)
    return response.content


# streaming
@traceable(name="stream_answer")
async def stream_answer(chunks: list[dict], question: str, history: list[dict]):

    llm = get_llm()
    context = format_context(chunks)
    messages = build_message(history, context, question)

    async for chunk in llm.astream(messages):
        yield chunk.content
