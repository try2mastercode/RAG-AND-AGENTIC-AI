import numpy as np

from retrieval.embeddings import _l2_normalize


def test_l2_normalize_unit_vector_length():
    vectors = np.array([[3.0, 4.0], [1.0, 0.0]])
    normalized = _l2_normalize(vectors)
    norms = np.linalg.norm(normalized, axis=-1)
    assert np.allclose(norms, [1.0, 1.0])


def test_l2_normalize_handles_zero_vector():
    vectors = np.array([[0.0, 0.0]])
    normalized = _l2_normalize(vectors)
    assert np.allclose(normalized, [[0.0, 0.0]])
