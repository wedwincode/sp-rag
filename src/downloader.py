from abc import ABC, abstractmethod
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from src.models import Document
from src.utils.logs import setup_logger


class AbstractDownloader(ABC):
    @abstractmethod
    def download_all(self) -> None:
        pass


class HTMLDownloader(AbstractDownloader):
    logger = setup_logger("html_downloader", "../logs/downloader.log")

    def __init__(self, documents: list[Document], output_dir: str = "../data/html",
                 selector: str = "div.field-item.even"):
        self.documents = documents
        self.output_dir = Path(output_dir)
        self.selector = selector

        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def download_all(self) -> None:
        for document in self.documents:
            if document.initial_url:
                downloaded_path = self._download_one(document.initial_url)
                if downloaded_path:
                    document.downloaded_path = downloaded_path

    def _download_one(self, url: HttpUrl) -> Path | None:
        url_as_str = str(url)
        self.logger.debug(f"Downloading {url_as_str}")
        try:
            response = requests.get(url_as_str, timeout=15)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(e)
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select_one(self.selector)

        if not items:
            self.logger.error(f"No items found on {url_as_str}")

        url_path = url.path[1:] if url.path and url.path.startswith("/") else url.path
        out_path = self.output_dir / f"{url_path}.html"
        out_path.write_text(str(items), encoding="utf-8")

        self.logger.debug(f"Downloaded {url_as_str}")

        return out_path
