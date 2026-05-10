from __future__ import annotations

import threading
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings


_lock = threading.Lock()
_vectorstore: FAISS | None = None


_DEFAULT_KNOWLEDGE = [
    "Course: Basic Math - Fee: $120/month - Age group: 6-10",
    "Course: Advanced Math - Fee: $160/month - Age group: 11-15",
    "Course: English Foundation - Fee: $110/month - Age group: 6-10",
    "Course: English Writing - Fee: $150/month - Age group: 11-15",
    "Assessment question math: What is 9 + 6? Answer: 15",
    "Assessment question english: Write one sentence using the word 'because'.",
]


def _load_pdf_docs(pdf_path: Path) -> list[Document]:
    if not pdf_path.exists():
        return [Document(page_content=text, metadata={"source": "fallback"}) for text in _DEFAULT_KNOWLEDGE]

    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    docs.extend(Document(page_content=text, metadata={"source": "seed"}) for text in _DEFAULT_KNOWLEDGE)
    return docs


def build_vectorstore() -> FAISS:
    docs = _load_pdf_docs(settings.tuition_pdf_path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100).split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)


def get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is None:
        with _lock:
            if _vectorstore is None:
                _vectorstore = build_vectorstore()
    return _vectorstore
