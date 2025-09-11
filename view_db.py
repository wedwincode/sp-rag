import chromadb
from chromadb.config import Settings

chroma_client = chromadb.HttpClient(host='localhost',
                                    port=8000,
                                    settings=Settings(anonymized_telemetry=False))

collection = chroma_client.get_or_create_collection("snip_chunks")

results = collection.get()

print("IDS:", results["ids"])
print("DOCS:", results["documents"])
print("METADATA:", results["metadatas"])
# print("EMBEDDINGS shape:", len(results["embeddings"]))
