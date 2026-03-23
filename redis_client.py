import logging
from app.core.config import settings

log = logging.getLogger(__name__)

class InMemoryCache:
    def __init__(self):
        self.store = {}

    def set(self, key, value, ex=None):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def exists(self, key):
        return key in self.store

    def delete(self, key):
        self.store.pop(key, None)

def _make_client():
    try:
        import redis
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        return client
    except Exception as exc:
        log.warning("Redis unavailable, falling back to in-memory cache: %s", exc)
        return InMemoryCache()

redis_client = _make_client()
