import numpy as np

from retrieval.embeddings import _l2_normalize, embed_text_for_image_query


def test_l2_normalize_unit_vector_length():
    vectors = np.array([[3.0, 4.0], [1.0, 0.0]])
    normalized = _l2_normalize(vectors)
    norms = np.linalg.norm(normalized, axis=-1)
    assert np.allclose(norms, [1.0, 1.0])


def test_l2_normalize_handles_zero_vector():
    vectors = np.array([[0.0, 0.0]])
    normalized = _l2_normalize(vectors)
    assert np.allclose(normalized, [[0.0, 0.0]])


def test_embed_text_for_image_query_truncates_long_text_instead_of_raising():
    # Regression test: CLIP's tokenizer has a hard 77-token limit and raises unless
    # truncate=True - this caught a real crash when a full LLM-generated user profile
    # (way over 77 tokens) was fed into the RAG Retriever's food_images query.
    long_text = "spicy vegan Vietnamese noodle soup with fresh herbs and lime " * 20
    result = embed_text_for_image_query([long_text])
    assert result.shape == (1, 512)
