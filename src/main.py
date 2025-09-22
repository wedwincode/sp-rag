import asyncio

from src.database import ChromaDBConnectorAsync
from src.generator import Generator
from src.models import Query
from src.settings import settings


async def run_pipeline():
    # docs = [
    #     # Document("http://sniprf.ru/sp25-13330-2012"),
    #     # Document("http://sniprf.ru/sp6-13130-2021"),
    #     Document("http://sniprf.ru/sp232-1311500-2015"),
    # ]
    #
    # downloader = HTMLDownloader(docs)
    # downloader.download_all()
    # # # doc = Document("http://sniprf.ru/sp25-13330-2012")
    # # # doc = Document("http://sniprf.ru/sp6-13130-2021")
    # # # doc.downloaded_path = Path("../data/html/sp25-13330-2012.html")
    # # # preprocessor = Preprocessor([doc])
    # preprocessor = Preprocessor(docs)
    # preprocessor.process_all()
    # preprocessor.generate_chunks()
    #
    # print(docs)

    db = ChromaDBConnectorAsync(host=settings.CHROMA_DB_HOST, port=settings.CHROMA_DB_PORT)
    # vectorizer = YandexVectorizer(docs, db)
    # await vectorizer.vectorize_all()

    # res = await db.get_collection("snip_chunks")
    # await db.delete_collection("snip_chunks")
    # print(await res.count())
    generator = Generator(db)
    while True:
        query = input("Введите вопрос: ")
        answer = await generator.generate_answer(Query(query))
        print("Ответ бота:\n" + answer.text)

if __name__ == '__main__':
    asyncio.run(run_pipeline())
