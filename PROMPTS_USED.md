# Prompts Used During Development

Below are representative prompts I used while developing and refining this project.  
Responses from the AI are not included.

---

## 1. FastAPI Deployment Clarification

"I am deploying a FastAPI app on AWS EC2. What is the correct uvicorn command for production without reload and with a single worker?"

Purpose:
To confirm best practice for running FastAPI in production on a low-memory instance.

---

## 2. systemd Service Configuration

"How do I create a systemd service file to run a FastAPI application using a virtual environment?"

Purpose:
To configure the app to restart automatically and remain live after SSH disconnect, i.e to make it live completely.

---

## 3. Security Group Debugging

"My EC2 instance is running uvicorn on port 8000, but the browser cannot access it. What security group rules should I change or verify?"

Purpose:
To ensure correct port exposure.

---

## 4. Prompt Refinement for Grounded QA

"My document-grounded assistant is rejecting some relevant questions. How can I make the system prompt less strict while still preventing hallucinations?"

Purpose:
To balance- avoiding hallucination and natural answer generation.

---

## 5. Retrieval Parameter Tuning

"For a document Q&A system using FAISS, what is a reasonable top-k value to reduce false negatives without increasing noise too much?"

Purpose:
To tune similarity search for better recall.

---

## 6. Chunking Strategy Discussion

"What are reasonable chunk_size and chunk_overlap values for CPU-based embedding using MiniLM models?"

Purpose:
To optimize indexing performance on a small EC2 instance.

---

## 7. README Structure Guidance

"What sections should a clean technical README include for a small RAG-based FastAPI project?"

Purpose:
To structure documentation professionally.

---

## 8. AI Usage Documentation

"How should I write an AI usage disclosure note that reflects minimal and responsible use of AI tools?"

Purpose:
To transparently document AI usage without overstating reliance.

---

## Notes
- API keys and secrets were never included in prompts.
