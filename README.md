---
title: Shiningace Ai Chat Backend
emoji: ⚡
colorFrom: red
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
short_description: chat boat backend for shiningace
---

# Tuition Management AI Chatbot (FastAPI + LangChain)

Standalone FastAPI app for Hugging Face Spaces deployment.

## Features
- `POST /webhook` endpoint with `{ "message": "...", "session_id": "..." }`
- Groq (`ChatGroq`) + LangChain RetrievalQA-style flow
- Local FAISS retriever with HuggingFace embeddings (`all-MiniLM-L6-v2`)
- PDF ingestion from `tuition_info.pdf` (falls back to built-in seed data if missing)
- Simple session-based assessment mode (math/english)
