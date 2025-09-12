
from src.downloader import HTMLDownloader
from src.models import Document
from src.preprocessor import Preprocessor


def run_pipeline():
    docs = [
        Document("http://sniprf.ru/sp25-13330-2012"),
        Document("http://sniprf.ru/sp6-13130-2021"),
    ]

    downloader = HTMLDownloader(docs)
    downloader.download_all()

    preprocessor = Preprocessor(docs)
    preprocessor.process_all()

    print(docs)


if __name__ == '__main__':
    run_pipeline()
