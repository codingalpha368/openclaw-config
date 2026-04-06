"""
RAG API - Retrieval Augmented Generation REST API
With continuous learning via feedback loops
"""

import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag-api")

# ── Config ──────────────────────────────────────────────
DATA_DIR   = Path("data/docs")
VECTOR_DIR = Path("data/chroma")
FEEDBACK_FILE = Path("data/feedback.jsonl")
API_KEY    = os.getenv("OPENAI_API_KEY", "")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
LLM_MODEL  = os.getenv("LLM_MODEL", "gpt-4o-mini")
COLLECTION = "rag-knowledge-base"

# ── Embeddings + Vector Store ───────────────────────────
embedding = OpenAIEmbeddings(model=EMBED_MODEL, api_key=API_KEY)

client = chromadb.PersistClient(
    path=str(VECTOR_DIR),
    settings=Settings(anonymized_telemetry=False)
)

vectorstore = Chroma(
    client=client,
    collection_name=COLLECTION,
    embedding_function=embedding,
)

# ── LLM ─────────────────────────────────────────────────
llm = ChatOpenAI(model=LLM_MODEL, api_key=API_KEY, temperature=0.3)

DEFAULT_PROMPT = PromptTemplate(
    template="""You are a helpful assistant. Use the provided context to answer the question.
If the answer is not in the context, say you don't know.

Context: {context}
Question: {question}
Answer:""",
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": DEFAULT_PROMPT},
    return_source_documents=True,
)

# ── FastAPI App ─────────────────────────────────────────
app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API with continuous learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ─────────────────────────────────────
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    include_sources: bool = True

class AskResponse(BaseModel):
    answer: str
    sources: Optional[list[dict]] = None
    confidence: float
    query_id: str

class FeedbackRequest(BaseModel):
    query_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class IngestResponse(BaseModel):
    ingested: int
    doc_ids: list[str]
    status: str

class HealthResponse(BaseModel):
    status: str
    documents_in_index: int
    model: str
    embed_model: str

# ── Helpers ─────────────────────────────────────────────
def get_doc_count() -> int:
    try:
        return vectorstore._collection.count()
    except Exception:
        return 0

def log_feedback(query_id: str, question: str, answer: str, rating: int, comment: Optional[str]):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_FILE, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}\t{query_id}\t{question}\t{answer}\t{rating}\t{comment or ''}\n")

# ── Endpoints ───────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        documents_in_index=get_doc_count(),
        model=LLM_MODEL,
        embed_model=EMBED_MODEL
    )

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    query_id = str(uuid.uuid4())[:8]

    try:
        result = qa_chain.invoke(
            {"query": req.question},
            config={"retriever": vectorstore.as_retriever(search_kwargs={"k": req.top_k})}
        )

        answer = result["result"]
        sources = []
        if req.include_sources and "source_documents" in result:
            for doc in result["source_documents"]:
                sources.append({
                    "content": doc.page_content[:500],
                    "source": doc.metadata.get("source", "unknown")
                })

        # Simple confidence proxy
        confidence = 0.9 if len(answer) > 50 else 0.6

        # Log for continuous learning
        log_feedback(query_id, req.question, answer, 0, None)

        return AskResponse(
            answer=answer,
            sources=sources if req.include_sources else None,
            confidence=confidence,
            query_id=query_id
        )
    except Exception as e:
        logger.error(f"Ask error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(req: FeedbackRequest):
    log_feedback(req.query_id, "", "", req.rating, req.comment)
    return {"status": "ok", "query_id": req.query_id}

@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / file.filename

    content = await file.read()
    dest.write_bytes(content)

    # Load & chunk
    suffix = dest.suffix.lower()
    if suffix == ".txt":
        loader = TextLoader(str(dest), encoding="utf-8")
    elif suffix == ".md":
        loader = DirectoryLoader(str(dest.parent), glob=str(dest.name), loader_cls=UnstructuredMarkdownLoader)
    else:
        # Fallback to text
        loader = TextLoader(str(dest), encoding="utf-8")

    try:
        docs = loader.load()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Load error: {e}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)

    # Add metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["filename"] = file.filename
        chunk.metadata["chunk_index"] = i

    # Embed & store
    try:
        vectorstore.add_documents(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {e}")

    return IngestResponse(
        ingested=len(chunks),
        doc_ids=[str(dest)],
        status="success"
    )

@app.get("/sources")
async def list_sources():
    """List all indexed documents."""
    try:
        count = get_doc_count()
        return {"documents_indexed": count, "collection": COLLECTION}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Run ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
