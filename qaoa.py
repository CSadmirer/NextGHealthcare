import logging
from typing import Any

from app.quantum.qubo import eval_qubo

log = logging.getLogger(__name__)

def _backend_name() -> str:
    try:
        import pyqpanda3  # noqa: F401
        return "qpanda3"
    except Exception:
        pass
    try:
        import qiskit  # noqa: F401
        return "qiskit"
    except Exception:
        pass
    return "classical"

QUANTUM_BACKEND = _backend_name()

def _classical_schedule(patients: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(patients, key=lambda x: (-int(x.get("priority", 1)), x.get("name", "")))
    return [{"slot": i + 1, **p} for i, p in enumerate(ordered)]

def run_qaoa(*args, **kwargs):
    return {}, None, None

def optimise_schedule(patients: list[dict[str, Any]]) -> dict[str, Any]:
    # Simple, reliable fallback. Quantum hooks are detected and can be extended later.
    schedule = _classical_schedule(patients)
    return {"backend": QUANTUM_BACKEND, "schedule": schedule, "note": "Classical stable fallback used."}
