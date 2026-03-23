import logging
from fastapi import Request
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "status": "error"})
