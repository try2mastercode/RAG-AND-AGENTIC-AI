import numpy as np

from retrieval import similarity


class FakeCollection:
    def __init__(self, response):
        self.response = response
        self.query_calls = []

    def query(self, **kwargs):
        self.query_calls.append(kwargs)
        return self.response


class FakeClient:
    def __init__(self, collection):
        self.collection = collection

    def get_collection(self, name):
        return self.collection


def test_retrieve_restaurants_computes_similarity_and_passes_filters(monkeypatch):
    response = {
        "ids": [["r001", "r002"]],
        "documents": [["doc a", "doc b"]],
        "metadatas": [[{"name": "A"}, {"name": "B"}]],
        "distances": [[0.1, 0.4]],
    }
    fake_collection = FakeCollection(response)
    monkeypatch.setattr(similarity, "get_client", lambda: FakeClient(fake_collection))
    monkeypatch.setattr(similarity, "embed_text", lambda texts: np.zeros((1, 384), dtype=np.float32))

    filters = {"cuisine": "Italian"}
    hits = similarity.retrieve_restaurants("a query", k=2, filters=filters)

    assert len(hits) == 2
    assert hits[0]["id"] == "r001"
    assert hits[0]["similarity"] == 0.9
    assert hits[1]["similarity"] == 0.6
    assert fake_collection.query_calls[0]["where"] == filters
    assert fake_collection.query_calls[0]["n_results"] == 2
