import numpy as np

def build_qubo(priorities: list[float], penalty: float = 8.0) -> np.ndarray:
    n = len(priorities)
    m = n * n
    q = np.zeros((m, m), dtype=float)

    def ix(i, j):
        return i * n + j

    for i in range(n):
        for j in range(n):
            q[ix(i, j), ix(i, j)] -= float(priorities[i]) * (n - j) / n

    for i in range(n):
        for j in range(n):
            q[ix(i, j), ix(i, j)] -= penalty
            for k in range(j + 1, n):
                q[ix(i, j), ix(i, k)] += 2 * penalty

    for j in range(n):
        for i in range(n):
            q[ix(i, j), ix(i, j)] -= penalty
            for m2 in range(i + 1, n):
                q[ix(i, j), ix(m2, j)] += 2 * penalty

    return q

def eval_qubo(Q: np.ndarray, x: list[int]) -> float:
    v = np.asarray(x, dtype=float)
    return float(v @ Q @ v)
