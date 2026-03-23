from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from app.core.redis_client import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
REVOKE_PREFIX = "revoked:jti:"
ATTEMPT_PREFIX = "login:attempts:"
LOCK_PREFIX = "login:lock:"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_token(subject: str, minutes: int, token_type: str = "access", extra: Optional[dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "jti": f"{subject}:{token_type}:{int(now.timestamp() * 1000)}",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    return create_token(subject, settings.ACCESS_TOKEN_TTL_MINUTES, "access", extra)

def create_refresh_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    return create_token(subject, settings.REFRESH_TOKEN_TTL_MINUTES, "refresh", extra)

def decode_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    jti = payload.get("jti")
    if jti and redis_client.exists(REVOKE_PREFIX + jti):
        raise JWTError("Token revoked")
    return payload

def revoke_token(token: str) -> None:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
    jti = payload.get("jti")
    if not jti:
        return
    exp = int(payload.get("exp", int(datetime.now(timezone.utc).timestamp()) + 60))
    ttl = max(exp - int(datetime.now(timezone.utc).timestamp()), 1)
    redis_client.set(REVOKE_PREFIX + jti, "1", ex=ttl)

def login_attempt_key(identifier: str) -> str:
    return f"{ATTEMPT_PREFIX}{identifier}"

def lock_key(identifier: str) -> str:
    return f"{LOCK_PREFIX}{identifier}"

def record_failed_login(identifier: str) -> int:
    key = login_attempt_key(identifier)
    current = int(redis_client.get(key) or 0) + 1
    redis_client.set(key, str(current), ex=settings.LOGIN_LOCKOUT_SECONDS)
    if current >= settings.MAX_FAILED_LOGINS:
        redis_client.set(lock_key(identifier), "1", ex=settings.LOGIN_LOCKOUT_SECONDS)
    return current

def clear_failed_logins(identifier: str) -> None:
    redis_client.delete(login_attempt_key(identifier))
    redis_client.delete(lock_key(identifier))

def is_locked(identifier: str) -> bool:
    return bool(redis_client.exists(lock_key(identifier)))
