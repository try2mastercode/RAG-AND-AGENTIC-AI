"""Creating Collections"""
#collection organizing data
import chromadb
from chromadb.utils import embedding_functions
ef=embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
client=chromadb.Client()
collection=client.create_collection(
    name="my_collection",
    metadata={"description":"A collection for storing user data"},
    configuration={
        "embedding_function":ef
    }
)
print(collection.name)
collection2=client.get_collection(name="my_collection")
print(collection2.metadata)
collection.modify(name="test2",metadata={"key":"value"})
print(collection.metadata)
collection.add(
    documents=[
        "hi, langchain",
        "hello llamaindex"
    ],
    metadatas=[
        {"source":"langchain.com","version":"0.2"},
        {"source":"llamaindex.ai","version":"0.12"}
    ],
    ids=["id1","id2"]
)
result=collection.get()
print(result["documents"],result["metadatas"])
print(collection.get())

print(collection.get(include=["embeddings"]))

print(collection.get(ids=["id1"]))

collection.update(
    ids=["id1"],
    metadatas=[{"source":"langchain.com","version":"0.3"}],
    documents=["hi, langchain updated"]
)
print(collection.get(ids=["id1"]))

collection.delete(where={"source":"llamaindex.ai"})
print(collection.get())

collection3=client.create_collection(
    name="hnsw_demo",
    configuration={
        "hnsw":{"space":"cosine"}
    }
)
print(collection3.name)