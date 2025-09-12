from pydantic import HttpUrl

from src.downloader import HTMLDownloader
from src.preprocessor import MarkdownPreprocessor


def run_pipeline():
    urls = [
        HttpUrl("http://sniprf.ru/sp25-13330-2012"),
        HttpUrl("http://sniprf.ru/sp6-13130-2021"),
    ]

    downloader = HTMLDownloader(urls)
    files_html = downloader.download_all()

    preprocessor = MarkdownPreprocessor(files_html)
    preprocessor.process_all()


if __name__ == '__main__':
    run_pipeline()
