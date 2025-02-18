import numpy as np
from numpy import dot
from numpy.linalg import norm


def cosine(A: np.array, B: np.array) -> float:
    """
    Basic function for cosine similarity.
    Use this for comparing embeddings.
    """
    return dot(A, B) / (norm(A) * norm(B))
