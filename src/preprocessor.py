import statistics
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
from bs4 import Tag
from html_to_markdown import convert_to_markdown
from matplotlib import pyplot as plt

from src.models import Document, Chunk
from src.settings import StageEnum, settings
from src.utils.logs import setup_logger


class AbstractPreprocessor(ABC):
    @abstractmethod
    def process_all(self) -> None:
        pass

    @abstractmethod
    def generate_chunks(self) -> None:
        pass


class Preprocessor(AbstractPreprocessor):
    logger = setup_logger("markdown_preprocessor", "../logs/preprocessor.log")

    def __init__(self, documents: list[Document], save_md: bool = True, output_dir: str = "../data/md"):
        self.documents = documents
        self.save_md = save_md
        self.output_dir = Path(output_dir)

        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def process_all(self) -> None:
        for document in self.documents:
            if document.downloaded_path:
                text, path = self._process_one(document.downloaded_path)
                document.text = text
                document.preprocessed_path = path

    def _process_one(self, path: Path) -> tuple[str, Path | None]:
        with open(path, 'r', encoding="utf-8") as f:
            result = convert_to_markdown(
                f.read(),
                custom_converters={  # type: ignore
                    "img": self.__link_converter,  # type: ignore
                    "table": self.__table_converter,  # type: ignore
                    "li": self.__li_converter  # type: ignore
                }
            )
            if not self.save_md:
                return result, None

            out_path = self.output_dir / path.name.replace(".html", ".md")
            out_path.write_text(result, encoding="utf-8")
            self.logger.debug(f"Processed {str(path)}")

            return result, out_path

    def generate_chunks(self, max_chunk_length: int = 500, min_chunk_length: int = 200) -> None:
        for document in self.documents:
            if document.text:
                split = [el.strip() for el in document.text.split("\n\n") if el.strip()]
                i = 0
                split_len = len(split)
                tables = []
                lengths_t = []
                cleared = []
                while i < split_len - 2:
                    if split[i] == "<<<TABLE_START>>>" and split[i + 2] == "<<<TABLE_END>>>":
                        tables.append(split[i + 1])
                        lengths_t.append(len(split[i + 1]))
                        i += 3
                    else:
                        cleared.append(split[i].strip())
                        i += 1

                buf = ""
                for para in cleared:
                    if len(para) > max_chunk_length:
                        parts = self.smart_split(para)
                        if len(buf) < min_chunk_length:
                            parts[0] = buf + " " + parts[0]
                        else:
                            document.chunks.append(Chunk(buf))
                        document.chunks.extend([Chunk(p) for p in parts])
                        buf = ""
                        continue

                    if len(buf) + len(para) + 1 <= max_chunk_length:
                        buf += " " + para if buf else para
                    else:
                        if len(buf) < min_chunk_length and document.chunks:
                            document.chunks[-1].text += " " + buf
                        else:
                            document.chunks.append(Chunk(buf))
                        buf = para

                if buf:
                    if len(buf) < min_chunk_length and document.chunks:
                        document.chunks[-1].text += " " + buf
                    else:
                        document.chunks.append(Chunk(buf))

                document.chunks.extend([Chunk(table) for table in tables])

                lengths = [len(c.text) for c in document.chunks]
                self.logger.debug(f"Total chunks for {document.name}: "
                                  f"{len(document.chunks)}, "
                                  f"min={min(lengths)}, "
                                  f"max={max(lengths)}, "
                                  f"median={statistics.median(lengths)}")

                if settings.STAGE == StageEnum.LOCAL:
                    df = pd.DataFrame(lengths, columns=["Длина"])
                    bins = range(0, 801, 50)
                    df["Интервал"] = pd.cut(df["Длина"], bins=bins, right=False)
                    counts = df["Интервал"].value_counts().sort_index()

                    counts.plot(kind="bar")
                    plt.xlabel("Интервалы длин")
                    plt.ylabel("Количество элементов")
                    plt.title("Распределение длин по интервалам")
                    plt.show()

    @staticmethod
    def smart_split(text: str, target_len=500, tolerance=50, min_remainder=100) -> list[str]:
        split = []
        start = 0
        n = len(text)

        while start < n:
            end = start + target_len
            if end >= n:
                split.append(text[start:].strip())
                break
            if n - end < min_remainder:
                split.append(text[start:].strip())
                break

            split_pos = text.rfind(".", start, end)
            if split_pos == -1:
                split_pos = text.rfind(" ", start, end)
            if split_pos == -1:
                split_pos = end

            if split_pos - start > target_len + tolerance:
                split_pos = start + target_len

            split.append(text[start:split_pos].strip())
            start = split_pos + 1
        return split

    @staticmethod
    def __link_converter(*, tag: Tag, text: str, **kwargs) -> str:
        site = "http://sniprf.ru"
        src = str(tag.get("src", ""))
        if not src.startswith(site):
            return f"![{text}]({site + src})"
        return f"![{text}]({src})"

    @staticmethod
    def __table_converter(*, tag: Tag, text: str, **kwargs) -> str:
        if tag.find("img"):
            imgs = []
            for img in tag.find_all("img"):
                if isinstance(img, Tag):
                    src = img.get("src")
                    if src:
                        imgs.append(str(src))
            if len(imgs) == 1:
                res = ""
                site = "http://sniprf.ru"
                for src in imgs:
                    if not src.startswith(site):
                        res += f"\n![table image]({site + src})"
                    else:
                        res += f"\n![table image]({src})"
                return res
        return f"\n\n<<<TABLE_START>>>\n\n{text}\n\n<<<TABLE_END>>>\n\n"

    @staticmethod
    def __li_converter(*, tag: Tag, text: str, **kwargs) -> str:
        return f"\n\n* {text}\n\n"

    # @staticmethod
    # def __list_generator(*, tag: Tag, text: str, **kwargs) -> str:
    #     number = text.split(".")[-1]
    #     if number.isdigit():
    #         return f"{number}."
    #     return f"{text}"
