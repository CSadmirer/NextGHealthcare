import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class ReadableFormatter(logging.Formatter):
    def format(self, record):
        return f"{self.formatTime(record)} {record.levelname:<8} {record.name} - {record.getMessage()}"

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return str(payload)

def setup_logging(debug: bool = False) -> None:
    Path("logs").mkdir(exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug else logging.INFO)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(ReadableFormatter() if debug else JsonFormatter())
    root.addHandler(console)

    app_log = RotatingFileHandler("logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
    app_log.setFormatter(ReadableFormatter())
    root.addHandler(app_log)

    err_log = RotatingFileHandler("logs/error.log", maxBytes=5 * 1024 * 1024, backupCount=3)
    err_log.setLevel(logging.ERROR)
    err_log.setFormatter(ReadableFormatter())
    root.addHandler(err_log)
