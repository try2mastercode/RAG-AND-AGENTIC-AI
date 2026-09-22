import chromadb

import config

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return _client


def reset_collection(name: str):
    """Deletes the collection if it already exists before recreating it, so rebuilding
    the index never leaves duplicate vector entries behind."""
    client = get_client()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    return client.create_collection(name, metadata={"hnsw:space": "cosine"})
