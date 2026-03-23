from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Tuple

from app.core.redis_client import redis_client
from app.models.appointment import Appointment
from app.services.appointment_service import create_appointment

SESSION_PREFIX = "wa:session:"

@dataclass
class WhatsAppSession:
    step: str = "start"
    data: Dict = field(default_factory=dict)

def _get_session(key: str) -> WhatsAppSession:
    raw = redis_client.get(SESSION_PREFIX + key)
    if not raw:
        return WhatsAppSession()
    try:
        import json
        obj = json.loads(raw)
        return WhatsAppSession(**obj)
    except Exception:
        return WhatsAppSession()

def _save_session(key: str, session: WhatsAppSession) -> None:
    import json
    redis_client.set(SESSION_PREFIX + key, json.dumps(session.__dict__), ex=3600)

def _clear_session(key: str) -> None:
    try:
        redis_client.delete(SESSION_PREFIX + key)
    except Exception:
        pass

def handle_message(from_number: str, text: str, db, clinic_id: int = 1) -> str:
    msg = (text or "").strip()
    session = _get_session(from_number)
    low = msg.lower()

    if low in {"help", "menu", "start"} and session.step == "start":
        return (
            "Reply with one of these:\n"
            "BOOK - book appointment\n"
            "CANCEL - cancel appointment\n"
            "RESCHEDULE - reschedule appointment\n"
            "HELP - see this menu"
        )

    if low == "book" and session.step == "start":
        session.step = "ask_name"
        _save_session(from_number, session)
        return "Please send patient full name."

    if session.step == "ask_name":
        session.data["full_name"] = msg
        session.step = "ask_phone"
        _save_session(from_number, session)
        return "Please send phone number."

    if session.step == "ask_phone":
        session.data["phone"] = msg
        session.step = "ask_age"
        _save_session(from_number, session)
        return "Please send age."

    if session.step == "ask_age":
        session.data["age"] = int(msg)
        session.step = "ask_reason"
        _save_session(from_number, session)
        return "Please send reason for visit."

    if session.step == "ask_reason":
        session.data["reason"] = msg
        session.step = "confirm"
        _save_session(from_number, session)
        return f"Confirm booking for {session.data['full_name']}? Reply YES to continue."

    if session.step == "confirm" and low == "yes":
        _clear_session(from_number)
        return "Booking flow received. Please use the clinic app to select date/time and confirm."

    return "Send HELP for options."
