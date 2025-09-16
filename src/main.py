import asyncio

from src.database import ChromaDBConnectorAsync
from src.downloader import HTMLDownloader
from src.models import Document
from src.preprocessor import Preprocessor
from src.settings import settings
from src.vectorizer import YandexVectorizer


async def run_pipeline():
    docs = [
        # Document("http://sniprf.ru/sp25-13330-2012"),
        Document("http://sniprf.ru/sp6-13130-2021"),
    ]

    downloader = HTMLDownloader(docs)
    downloader.download_all()
    # # doc = Document("http://sniprf.ru/sp25-13330-2012")
    # # doc = Document("http://sniprf.ru/sp6-13130-2021")
    # # doc.downloaded_path = Path("../data/html/sp25-13330-2012.html")
    # # preprocessor = Preprocessor([doc])
    preprocessor = Preprocessor(docs)
    preprocessor.process_all()
    preprocessor.generate_chunks()

    print(docs)

    db = ChromaDBConnectorAsync(host=settings.CHROMA_DB_HOST, port=settings.CHROMA_DB_PORT)
    vectorizer = YandexVectorizer(docs, db)
    await vectorizer.vectorize_all()

    res = await db.get_collection("snip_chunks")
    # await db.delete_collection("snip_chunks")
    print(await res.count())


if __name__ == '__main__':
    asyncio.run(run_pipeline())
