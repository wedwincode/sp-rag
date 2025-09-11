import re
from pathlib import Path


def preprocess_snip_text(text: str) -> list[str]:
    # Убираем пустые строки
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    formula_pattern = re.compile(r"[=√Σ∑±/*]")
    lines = [line for line in lines if not formula_pattern.search(line)]

    lines = [line for line in lines if not line.lower().startswith("таблица")]
    lines = [line for line in lines if "|" not in line and "\t" not in line]

    clean_text = "\n".join(lines)

    chunk_pattern = re.compile(r"(?=\n?\d+(\.\d+)+\s)")
    clean_chunks = [chunk.strip() for chunk in chunk_pattern.split(clean_text) if chunk.strip()]

    return clean_chunks


# === Пример использования ===
md_text = Path("output.md").read_text(encoding="utf-8")
chunks = preprocess_snip_text(md_text)

for i, chunk in enumerate(chunks[:5], start=1):
    print(f"--- Чанк {i} ---\n{chunk}\n")
