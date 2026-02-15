# Private Knowledge Q&A (Mini Workspace)

A document-grounded Q&A web application that allows users to upload text documents, index them, and ask questions strictly based on the uploaded content.

This project implements a persistent Retrieval-Augmented Generation (RAG) system with document storage, vector indexing, and source attribution.

---

## Features

- Home page and Status page
- Upload one or more `.txt` documents
- Persistent FAISS vector index
- Duplicate document detection (via SHA256 hash)
- Ask questions grounded strictly in uploaded documents
- Display answer sources with snippets
- Health check endpoint
- Persistent document registry
- Production deployment on AWS EC2

---

## How It Works

1. **Upload**
   - Documents are stored in the `uploads/` directory.
   - Each file is hashed to prevent duplicate indexing.
   - Text is split into chunks.
   - Chunks are embedded using a sentence-transformer model.
   - Vectors are stored in a persistent FAISS index.

2. **Query**
   - User question is embedded.
   - Top-k relevant chunks are retrieved.
   - Context is passed to an LLM (Groq llama-3.1-8b-instant").
   - The model answers strictly using provided context.
   - Relevant source snippets are returned.

3. **Persistence**
   - FAISS index stored on disk.
   - Document registry stored in `data/documents.json`.
   - Survives restarts and redeployments.

---

## Tech Stack

- FastAPI
- Uvicorn
- FAISS (vector store)
- Sentence-Transformers (embeddings)
- Groq API (Llama 3.1 8B Instruct)
- AWS EC2 (deployment)

---

## Environment Variables

- Created a `.env` file:
- Used GROQ_API_KEY

## Running Locally

### 1. Clone the repository
git clone <https://github.com/Sree-Vardhan-Reddy-K>
cd <Aggroso_Private_Knowledge_Q-A>

### 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the server
uvicorn app.api:app --reload
Server will run at:
http://localhost:8000

## 5. Production Deployment (EC2)
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 1

For persistent background execution, a `systemd` service is configured.

## Health Endpoint

GET /health
Returns:
- Backend status
- Vector store load status
- LLM connectivity status

## 📂 Project Structure

app/
api.py
rag_service.py

uploads/
faiss_index/
data/
documents.json

## What Is Implemented

- Persistent document storage
- Duplicate detection
- Chunking + embedding
- Similarity retrieval
- Context-grounded answering
- Source snippet attribution
- Health check endpoint
- AWS EC2 deployment
- Background service (systemd)

## Example Usage Flow
1. Upload documents.
2. Confirm they appear in indexed list.
3. Ask a question.
4. Receive answer with source snippets.
5. Check system health at `/health`.

## 📌 Live Deployment

Hosted on AWS EC2.
Live link:
http://ec2-18-60-154-210.ap-south-2.compute.amazonaws.com:8000/

