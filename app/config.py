from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    odoo_url: str = os.getenv("ODOO_URL", "")
    odoo_db: str = os.getenv("ODOO_DB", "")
    odoo_username: str = os.getenv("ODOO_USERNAME", "")
    odoo_password: str = os.getenv("ODOO_PASSWORD", "")

    tuition_pdf_path: Path = Path(os.getenv("TUITION_PDF_PATH", BASE_DIR / "tuition_info.pdf"))


settings = Settings()
