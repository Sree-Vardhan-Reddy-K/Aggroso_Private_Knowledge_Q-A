import os
import json
from typing import List, Tuple

from dotenv import load_dotenv
from groq import Groq

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

client = Groq(api_key=GROQ_API_KEY)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")
DOC_REGISTRY_PATH = os.path.join(BASE_DIR, "data", "documents.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DOC_REGISTRY_PATH), exist_ok=True)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_registry():
    if not os.path.exists(DOC_REGISTRY_PATH):
        return []
    with open(DOC_REGISTRY_PATH, "r") as f:
        return json.load(f)


def save_registry(docs):
    with open(DOC_REGISTRY_PATH, "w") as f:
        json.dump(docs, f, indent=2)


def load_vectorstore():
    faiss_file = os.path.join(INDEX_DIR, "index.faiss")
    if os.path.exists(faiss_file):
        return FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    return None


def save_vectorstore(vectorstore):
    vectorstore.save_local(INDEX_DIR)


def add_documents(file_paths: List[str]) -> int:
    # Step 1: Save files to uploads already handled in API

    # Step 2: Get ALL uploaded files
    all_files = [
        os.path.join(UPLOAD_DIR, f)
        for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".txt")
    ]

    if not all_files:
        raise ValueError("No documents found in upload directory.")

    documents = []

    for path in all_files:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            if not text.strip():
                continue

        doc = Document(
            page_content=text,
            metadata={"source": os.path.basename(path)}
        )
        documents.append(doc)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=100
    )

    splits = splitter.split_documents(documents)
    if not splits:
        raise ValueError("Uploaded documents contain no usable text.")

    # Step 3: Always rebuild FAISS index from scratch
    vectorstore = FAISS.from_documents(splits, embeddings)

    save_vectorstore(vectorstore)

    # Step 4: Update registry deterministically
    registry = [os.path.basename(p) for p in all_files]
    save_registry(registry)

    return len(file_paths)



def list_documents():
    return load_registry()


def query_documents(question: str) -> Tuple[str, List[dict]]:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    vectorstore = load_vectorstore()
    if not vectorstore:
        raise ValueError("No documents indexed")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        return "No relevant information found.", []

    context = "\n\n".join([d.page_content for d in retrieved_docs])

    system_prompt = (
        "You are a document assistant. "
        "Answer only and only using the provided context. "
        "If the answer is not present, say you cannot find it." 
        "If the answer is not present in the provided documents, outright say cannot find the information in the provided context"
        "Reject general questions which are irrelevant from the documents provided, for example - weather today, how to make pizza, does the sun rise east or west etc"
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0,
        max_tokens=800
    )

    answer = response.choices[0].message.content.strip()

    sources = []
    for doc in retrieved_docs:
        sources.append({
            "document": doc.metadata.get("source"),
            "snippet": doc.page_content[:500]
        })

    return answer, sources


def health_check():
    try:
        vectorstore = load_vectorstore()
        llm_status = "ok"
        client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Ping"}],
            max_tokens=1
        )
    except Exception:
        llm_status = "error"

    return {
        "backend": "ok",
        "vector_store_loaded": bool(vectorstore),
        "llm_connection": llm_status
    }
