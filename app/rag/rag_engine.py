import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer


from app.core.config import settings
from app.rag.db_agent import get_database_response
from app.rag.knowledge_base import DOCUMENTS

# Paths
CHROMA_DIR = Path(__file__).parent / "chroma_store"
COLLECTION_NAME = "rohana_credit_kb"

# Lazy-loaded singletons
_model = None
_collection = None
_groq_client = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection(COLLECTION_NAME)
        if _collection.count() == 0:
            _build_index()
    return _collection


def _build_index():
    print("Building RAG index... (first run only)")
    model = _get_model()
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(COLLECTION_NAME)

    texts = [doc["text"] for doc in DOCUMENTS]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=[doc["id"] for doc in DOCUMENTS],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"topic": doc["topic"]} for doc in DOCUMENTS],
    )
    print(f"RAG index built: {len(DOCUMENTS)} documents indexed.")


def rebuild_index():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _build_index()
    global _collection
    _collection = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=settings.groq_api_key)
    return _groq_client


def preload():
    _get_model()
    _get_collection()
    _get_groq_client()


def retrieve(query: str, n_results: int = 4) -> list[str]:
    model = _get_model()
    collection = _get_collection()
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count()),
    )
    return results["documents"][0] if results["documents"] else []


def chat(question: str, history: list[dict], db=None) -> str:
    """
    Full RAG pipeline:
    1. Check database-specific queries first
    2. Retrieve relevant chunks from ChromaDB
    3. Build a prompt with context + conversation history
    4. Ask Groq (llama-3.3-70b) to answer
    """
    if db is not None:
        db_answer = get_database_response(question, db)
        if db_answer is not None:
            return db_answer

    client = _get_groq_client()

    # Step 1: retrieve relevant context
    chunks = retrieve(question)
    context = "\n\n---\n\n".join(chunks) if chunks else "No relevant context found."

    # Step 2: system prompt with retrieved context baked in
    system_prompt = f"""You are a helpful assistant for Rohana Credit, a loan management system.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I don't have information about that in my knowledge base."
Be concise, friendly, and practical. Use bullet points for steps or lists.

CONTEXT:
{context}"""

    # Step 3: build messages list (last 6 messages for context)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1024,
        temperature=0.3,
    )

    return response.choices[0].message.content