from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from yandex_cloud_ml_sdk import YCloudML
from chromadb.config import Settings

from src.settings import settings

MODEL_URI = f"emb://{settings.YC_FOLDER_ID}/text-search-doc/latest"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
md_text = Path("output.md").read_text(encoding="utf-8")

chunks = text_splitter.split_text(md_text)
chunk_objs = [
    {"id": f"chunk_{i}", "text": text, "meta": {"source": "output.md", "chunk": i}}
    for i, text in enumerate(chunks)
]
print(chunk_objs)
print(f"Количество чанков: {len(chunks)}")

sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
model = sdk.models.text_embeddings("doc")

chroma_client = chromadb.HttpClient(host='localhost',
                                    port=8000,
                                    settings=Settings(anonymized_telemetry=False))

collection = chroma_client.get_or_create_collection("snip_chunks")

for chunk in chunk_objs:
    response = model.run(chunk["text"])
    vector = list(response.embedding)
    print(vector)
    collection.add(
        ids=[chunk["id"]],
        documents=[chunk["text"]],
        embeddings=[vector],
        metadatas=[chunk["meta"]]
    )

print("All chunks saved to ChromaDB")

results = collection.get()

print("IDS:", results["ids"])
print("DOCS:", results["documents"])
print("METADATA:", results["metadatas"])
# print("EMBEDDINGS shape:", len(results["embeddings"]))
