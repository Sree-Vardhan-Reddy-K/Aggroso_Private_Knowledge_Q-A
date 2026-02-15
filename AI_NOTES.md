# AI Notes

I built this project primarily through manual design and implementation. I used AI tools selectively to speed up specific parts of development, clarify edge cases, and debug infrastructure issues — not to generate the entire system blindly.

---- 

## Where I Used AI

I used ChatGPT in a limited and targeted way for:

- Clarifying FastAPI configuration and systemd deployment setup.
- Debugging EC2 networking and security group configuration.
- Refining the system prompt to reduce over-rejection of relevant questions.
- Improving documentation structure (README formatting and clarity).
- In Exception Handling i.e wherever exceptions may arise & are needed, because it helps in debugging

I did not rely on AI to design the system architecture. I wrote and structured the core logic myself.

---

## What I Designed and Verified Myself

I manually implemented and tested:

- SHA256-based duplicate document detection.
- Persistent FAISS vector index storage.
- Document registry (`documents.json`) for tracking uploaded files.
- Chunking strategy and tuning (chunk size and overlap).
- Similarity-based retrieval configuration (top-k tuning).
- Context construction and source snippet extraction.
- Strict document-grounded answer enforcement.
- Health check endpoint.
- AWS EC2 deployment and systemd service setup.

I tested all major flows first locally and then on EC2 to ensure correctness and stability.

---

## LLM and Provider Choice

I used:

**Model:** Llama-3.1-8b-instant
**Provider:** Groq API  

I chose Groq because it provides low-latency inference, reliable hosted access, and avoids the need for local GPU infrastructure. It fits well for a lightweight production-style deployment.

The LLM is used only for answer generation after retrieval. All retrieval, filtering, and context control are handled before calling the model.

---

## Embedding Model

For embeddings, I used:

`sentence-transformers/all-MiniLM-L6-v2`

I chose this model because it is lightweight, CPU-friendly, and provides good semantic retrieval performance for document-based Q&A tasks.

---

## My Approach to AI Usage

I treat AI tools as assistants for debugging and refinement rather than as substitutes for understanding. I made sure I understood and verified all core logic before deployment.
