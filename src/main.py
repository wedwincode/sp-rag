from pydantic import HttpUrl

from src.downloader import HTMLDownloader


def run_pipeline():
    urls = [
        HttpUrl("http://sniprf.ru/sp25-13330-2012"),
        HttpUrl("http://sniprf.ru/sp6-13130-2021"),
    ]
    downloader = HTMLDownloader(urls)

    downloader.download()


if __name__ == '__main__':
    run_pipeline()
