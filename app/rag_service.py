import os
import re
import json
import hashlib
from typing import List, Tuple

from dotenv import load_dotenv
from groq import Groq

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ---------------------------------------------------
# Environment & Setup
# ---------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "documents.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# ---------------------------------------------------
# Utilities
# ---------------------------------------------------

def compute_file_hash(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return []
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def load_vectorstore():
    index_file = os.path.join(INDEX_DIR, "index.faiss")
    if os.path.exists(index_file):
        return FAISS.load_local(
            INDEX_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return None


def save_vectorstore(vectorstore):
    vectorstore.save_local(INDEX_DIR)


# ---------------------------------------------------
# Core Logic
# ---------------------------------------------------

def add_documents(file_paths: List[str]) -> dict:
    registry = load_registry()
    existing_hashes = {doc["hash"] for doc in registry}

    new_documents = []
    added_files = []
    skipped_files = []

    for path in file_paths:
        file_hash = compute_file_hash(path)

        if file_hash in existing_hashes:
            skipped_files.append(os.path.basename(path))
            continue

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if not text.strip():
            continue

        new_documents.append(
            Document(
                page_content=text,
                metadata={"source": os.path.basename(path)}
            )
        )

        added_files.append({
            "filename": os.path.basename(path),
            "hash": file_hash
        })

    if not new_documents:
        return {
            "added": [],
            "skipped": skipped_files
        }

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=100
    )

    splits = splitter.split_documents(new_documents)

    if not splits:
        return {
            "added": [],
            "skipped": skipped_files
        }

    vectorstore = load_vectorstore()

    if vectorstore:
        vectorstore.add_documents(splits)
    else:
        vectorstore = FAISS.from_documents(splits, embeddings)

    save_vectorstore(vectorstore)

    registry.extend(added_files)
    save_registry(registry)

    return {
        "added": [doc["filename"] for doc in added_files],
        "skipped": skipped_files
    }


def list_documents():
    registry = load_registry()
    return [doc["filename"] for doc in registry]


def query_documents(question: str) -> Tuple[str, List[dict]]:
    refusal_text = "The answer is not present in the uploaded documents."

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    vectorstore = load_vectorstore()
    if not vectorstore:
        raise ValueError("No documents indexed.")

    # Retrieve top 5 relevant chunks
    retrieved_docs = vectorstore.similarity_search(question, k=5)

    if not retrieved_docs:
        return refusal_text, []

    # Build context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    system_prompt = (
        "You are a strict document-grounded assistant.\n"
        "Answer ONLY using the provided context.\n"
        "If the answer is not explicitly present in the context,\n"
        f"respond exactly with: '{refusal_text}'\n"
        "Do not use external knowledge.\n"
        "Do not infer beyond the context.\n"
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0,
        max_tokens=1200
    )

    answer = response.choices[0].message.content.strip()

    # Only suppress sources if explicit refusal
    if answer == refusal_text:
        return answer, []

    # Build sources
    sources = []
    for doc in retrieved_docs:
        full_text = doc.page_content.strip()
        max_chars = 1500

        if len(full_text) <= max_chars:
            snippet = full_text
        else:
            temp = full_text[:max_chars]
            last_period = max(
                temp.rfind("."),
                temp.rfind("?"),
                temp.rfind("!")
            )
            if last_period != -1:
                snippet = temp[:last_period + 1]
            else:
                snippet = temp

        sources.append({
            "document": doc.metadata.get("source"),
            "snippet": snippet.strip()
        })

    return answer, sources


def health_check():
    try:
        client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Ping"}],
            max_tokens=1
        )
        llm_status = "ok"
    except Exception:
        llm_status = "error"

    vectorstore_loaded = load_vectorstore() is not None

    return {
        "backend": "ok",
        "vector_store_loaded": vectorstore_loaded,
        "llm_connection": llm_status
    }
