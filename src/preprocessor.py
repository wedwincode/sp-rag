from abc import ABC, abstractmethod
from pathlib import Path

from bs4 import Tag
from html_to_markdown import convert_to_markdown

from src.models import Document
from src.utils.logs import setup_logger


class AbstractPreprocessor(ABC):
    @abstractmethod
    def process_all(self) -> None:
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
                custom_converters={"img": self.__link_converter}  # type: ignore
                # "b": self.__list_generator
            )
            if not self.save_md:
                return result, None

            out_path = self.output_dir / path.name.replace(".html", ".md")
            out_path.write_text(result, encoding="utf-8")
            self.logger.debug(f"Processed {str(path)}")

            return result, out_path

    @staticmethod
    def __link_converter(*, tag: Tag, text: str, **kwargs) -> str:
        site = "http://sniprf.ru"
        src = str(tag.get("src", ""))
        if not src.startswith(site):
            return f"![{text}]({site + src})"
        return f"![{text}]({src})"

    # @staticmethod
    # def __list_generator(*, tag: Tag, text: str, **kwargs) -> str:
    #     number = text.split(".")[-1]
    #     if number.isdigit():
    #         return f"{number}."
    #     return f"{text}"
