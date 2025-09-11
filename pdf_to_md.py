from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

pdf_path = "sp_24.13330.2011.pdf"
loader = PyPDFLoader(pdf_path)
documents = loader.load()

md_text = ""
for i, doc in enumerate(documents, start=1):
    md_text += f"\n\n# Страница {i}\n\n{doc.page_content}\n"

Path("output.md").write_text(md_text, encoding="utf-8")
print("PDF converted to output.md")
