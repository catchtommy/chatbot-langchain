from __future__ import annotations

import logging
import re
import xmlrpc.client
from dataclasses import dataclass

from app.config import settings


logger = logging.getLogger(__name__)
_PHONE_PATTERN = r"\+?\d[\d\s-]{8,}\d"


@dataclass
class ContactInfo:
    name: str | None = None
    email: str | None = None
    phone: str | None = None


def extract_contact_info(message: str) -> ContactInfo | None:
    email = None
    for token in message.replace("\n", " ").split():
        cleaned = token.strip(".,;:!?()[]{}<>\"'")
        if "@" not in cleaned or cleaned.count("@") != 1:
            continue
        local, domain = cleaned.split("@")
        if local and "." in domain and not domain.startswith(".") and not domain.endswith("."):
            email = cleaned
            break

    # Accepts basic international/local patterns with 8+ digits (e.g., "+1 555-123-4567", "0912 345 6789").
    phone_match = re.search(_PHONE_PATTERN, message)
    name_match = re.search(r"(?:i am|i'm|name is)\s+([A-Za-z][A-Za-z\s'-]{1,40})", message, re.IGNORECASE)

    info = ContactInfo(
        name=name_match.group(1).strip() if name_match else None,
        email=email,
        phone=phone_match.group(0).strip() if phone_match else None,
    )
    if not info.email and not info.phone:
        return None
    return info


class OdooClient:
    def __init__(self) -> None:
        self._enabled = all((settings.odoo_url, settings.odoo_db, settings.odoo_username, settings.odoo_password))

    def _authenticate(self) -> tuple[int, xmlrpc.client.ServerProxy] | None:
        if not self._enabled:
            return None

        try:
            common = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/common")
            uid = common.authenticate(settings.odoo_db, settings.odoo_username, settings.odoo_password, {})
            if not uid:
                logger.warning("Odoo authentication failed")
                return None
            models = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/object")
            return uid, models
        except OSError as exc:
            logger.warning("Odoo unavailable: %s", exc)
            return None

    def create_or_update_lead(self, contact: ContactInfo, note: str | None = None) -> int | None:
        auth = self._authenticate()
        if auth is None:
            return None
        uid, models = auth

        values = {
            "name": f"Parent inquiry - {contact.name or contact.email or contact.phone}",
            "contact_name": contact.name or "Parent",
            "email_from": contact.email,
            "phone": contact.phone,
            "description": note or "Lead created from chatbot webhook",
        }

        try:
            return models.execute_kw(
                settings.odoo_db,
                uid,
                settings.odoo_password,
                "crm.lead",
                "create",
                [values],
            )
        except OSError as exc:
            logger.warning("Failed creating lead in Odoo: %s", exc)
            return None

    def update_assessment_note(self, lead_id: int, result_note: str) -> bool:
        auth = self._authenticate()
        if auth is None:
            return False
        uid, models = auth

        try:
            return bool(
                models.execute_kw(
                    settings.odoo_db,
                    uid,
                    settings.odoo_password,
                    "crm.lead",
                    "write",
                    [[lead_id], {"description": result_note}],
                )
            )
        except OSError as exc:
            logger.warning("Failed updating assessment in Odoo: %s", exc)
            return False
