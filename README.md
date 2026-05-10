# Tuition Management AI Chatbot (FastAPI + LangChain)

Standalone FastAPI app for Hugging Face Spaces deployment.

## Features
- `POST /webhook` endpoint with `{ "message": "...", "session_id": "..." }`
- Groq (`ChatGroq`) + LangChain RetrievalQA-style flow
- Local FAISS retriever with HuggingFace embeddings (`all-MiniLM-L6-v2`)
- PDF ingestion from `tuition_info.pdf` (falls back to built-in seed data if missing)
- Simple session-based assessment mode (math/english)
- Odoo XML-RPC integration for `crm.lead` creation and assessment updates

## Project layout
- `app/main.py` - FastAPI app and routes
- `app/config.py` - environment-based configuration
- `app/rag.py` - PDF loading, chunking, embedding, FAISS initialization
- `app/chatbot_service.py` - orchestrates assessment, RAG answer flow, Odoo side effects
- `app/assessment.py` - deterministic assessment state + grading logic
- `app/odoo_client.py` - resilient Odoo XML-RPC client and contact extraction

## Environment variables
Copy `.env.example` and set values:
- `GROQ_API_KEY`
- `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`
- Optional: `TUITION_PDF_PATH`

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Hugging Face Spaces
Use FastAPI SDK and set startup command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

Add `tuition_info.pdf` at repository root (or set `TUITION_PDF_PATH`) to ground responses with your tuition content.
