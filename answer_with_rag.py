import chromadb
from chromadb.config import Settings
from yandex_cloud_ml_sdk import YCloudML

from src.settings import settings


chroma_client = chromadb.HttpClient(host='localhost',
                                    port=8000,
                                    settings=Settings(anonymized_telemetry=False))
collection = chroma_client.get_or_create_collection("snip_chunks")

sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
query_model = sdk.models.text_embeddings("query")
# TODO: async
gpt_model = sdk.models.completions("yandexgpt")
gpt_model.configure(temperature=0.3, max_tokens=300)

user_question = input("Введите вопрос:")

q_response = query_model.run(user_question)
query_vector = list(q_response.embedding)

search_results = collection.query(
    query_embeddings=[query_vector],
    n_results=4,
    include=["documents", "metadatas"]
)

print("\nНайденные чанки: ")
for i, (doc, meta) in enumerate(zip(search_results["documents"][0], search_results["metadatas"][0]), start=1):
    # print(f"\n--- Чанк {i} ---")
    # print(doc[:500], "..." if len(doc) > 500 else "")
    # print("Источник:", meta)
    print(f"chunk_{i}")


context_parts = []
for doc, meta in zip(search_results["documents"][0], search_results["metadatas"][0]):
    source = f'{meta.get("source")} (chunk {meta.get("chunk")})'
    context_parts.append(f"{doc}\nИсточник: {source}")

context_text = "\n\n".join(context_parts)

prompt = f"""
Вопрос пользователя: {user_question}

Контекст из СНиПов/СП:
{context_text}

Ответь на вопрос, используя только эти данные. 
В конце обязательно укажи источник.
"""

# print("=== PROMPT ===")
# print(prompt)


completion = gpt_model.run(prompt)

print("\n=== ОТВЕТ БОТА ===")
print(completion.text)
