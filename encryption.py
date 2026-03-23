import logging
from cryptography.fernet import Fernet
from app.core.config import settings

log = logging.getLogger(__name__)

class FieldCipher:
    def __init__(self, key: str):
        if not key:
            log.warning("ENCRYPTION_KEY not set; generating ephemeral in-memory key for this runtime.")
            key = Fernet.generate_key().decode()
        self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except Exception:
            return None

cipher = FieldCipher(settings.ENCRYPTION_KEY)
