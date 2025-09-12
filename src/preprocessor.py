import logging
from abc import ABC, abstractmethod
from pathlib import Path

from bs4 import Tag
from html_to_markdown import convert_to_markdown

from src.utils.logs import setup_logger


class AbstractPreprocessor(ABC):
    @abstractmethod
    def process_all(self):
        pass


class MarkdownPreprocessor(AbstractPreprocessor):
    logger = setup_logger("markdown_preprocessor", "../logs/preprocessor.log")

    def __init__(self, html_paths: list[Path], output_dir: str = "../data/md"):
        self.paths = html_paths
        self.output_dir = Path(output_dir)

        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def process_all(self) -> list[Path]:
        out_paths: list[Path] = []
        for path in self.paths:
            out_path = self._process_one(path)
            if out_path:
                out_paths.append(out_path)

        return out_paths

    def _process_one(self, path: Path) -> Path | None:
        with open(path, 'r', encoding="utf-8") as f:
            result = convert_to_markdown(
                f.read(),
                custom_converters={"img": self.__link_converter}  # type: ignore[arg-type]
            )
            out_path = self.output_dir / path.name.replace(".html", ".md")
            out_path.write_text(result, encoding="utf-8")
            self.logger.debug(f"Processed {str(path)}")

            return out_path

    @staticmethod
    def __link_converter(*, tag: Tag, text: str, **kwargs) -> str:
        site = "http://sniprf.ru"
        src = str(tag.get("src", ""))
        if not src.startswith(site):
            return f"![{text}]({site + src})"
        return f"![{text}]({src})"
