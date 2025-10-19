import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from sp_rag.models import Document
from sp_rag.utils.logs import setup_logger


class AbstractDownloader(ABC):
    @abstractmethod
    def download_all(self) -> None:
        pass


class HTMLDownloader(AbstractDownloader):
    logger: logging.Logger
    _log_file: str = "downloader.log"

    def __init__(self, documents: list[Document], output_dir: str = "../data/html",
                 selector: str = "div.field-item.even"):
        self.documents = documents
        self.output_dir = Path(output_dir)
        self.selector = selector

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if HTMLDownloader.logger is None:
            HTMLDownloader.logger = setup_logger("html_downloader", "downloader.log")

    @classmethod
    def set_log_file(cls, log_file: str):
        cls._log_file = log_file
        cls.logger = setup_logger("html_downloader", log_file)

    def download_all(self) -> None:
        for document in self.documents:
            if document.initial_url:
                downloaded_path, name = self._download_one(document.initial_url)
                if downloaded_path:
                    document.downloaded_path = downloaded_path
                if name:
                    document.name = name

    def _download_one(self, url: HttpUrl) -> tuple[Path | None, str | None]:
        url_as_str = str(url)
        self.logger.debug(f"Downloading {url_as_str}")
        try:
            response = requests.get(url_as_str, timeout=15)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(e)
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select_one(self.selector)
        heading = soup.select_one("h1#page-title")
        name = heading.text.strip() if heading else None

        if not items:
            self.logger.error(f"No items found on {url_as_str}")

        url_path = url.path[1:] if url.path and url.path.startswith("/") else url.path
        out_path = self.output_dir / f"{url_path}.html"
        out_path.write_text(str(items), encoding="utf-8")

        self.logger.debug(f"Downloaded {url_as_str} ({name}")

        return out_path, name
