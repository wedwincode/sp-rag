# SP-RAG

This project implements a Retrieval-Augmented Generation (RAG) pipeline for working with Russian construction norms and regulations (SNiP, SP).

## Planned features

- Parsing documents (PDF/HTML) and converting them to Markdown.

- Text chunking by sections or fixed length.

- Vectorization of chunks using Yandex Cloud ML SDK embeddings.

- Storing vectors in ChromaDB for semantic search.

- Query handling: embedding user questions, retrieving the most relevant chunks, and passing them to YandexGPT for answer generation with source references.

- Support for Markdown tables.

## Stack

- Python 3.12

- Yandex Cloud ML SDK

- ChromaDB

- LangChain (for text splitting and orchestration)

- BeautifulSoup (for HTML preprocessing)