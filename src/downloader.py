import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from pydantic import HttpUrl


class AbstractDownloader(ABC):
    @abstractmethod
    def download(self) -> None:
        pass


class HTMLDownloader(AbstractDownloader):
    logging.basicConfig(filename="../logs/downloader.log",
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()

    def __init__(self, urls: list[HttpUrl], output_dir: str = "../data/pages"):
        self.urls = urls
        self.output_dir = Path(output_dir)

        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def download(self) -> None:
        for i, url in enumerate(self.urls, start=1):
            self._download_url(url, i)

    def _download_url(self, url: HttpUrl, idx: int) -> None:
        url_as_str = str(url)
        self.logger.debug(f"{idx}/{len(self.urls)} Downloading {url_as_str}")
        try:
            response = requests.get(url_as_str, timeout=15)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(e)
            return

        url_path = url.path[1:] if url.path and url.path.startswith("/") else url.path
        out_path = self.output_dir / f"{url_path}.html"
        out_path.write_text(response.text, encoding="utf-8")

        self.logger.debug(f"{idx}/{len(self.urls)} Downloaded {url_as_str}")
