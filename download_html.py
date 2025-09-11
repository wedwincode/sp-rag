import requests
from bs4 import BeautifulSoup
from pathlib import Path

from pydantic import HttpUrl


def download_field_items(urls: list[HttpUrl], out_dir="pages"):
    """
    Скачивает страницы по ссылкам, достает содержимое div.field-items
    и сохраняет в html файлы.

    :param urls: список ссылок
    :param out_dir: папка для сохранения файлов
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] Скачиваю {str(url)}...")
        try:
            response = requests.get(str(url), timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Ошибка при скачивании {str(url)}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        field_items = soup.select_one("div.field-items")

        if not field_items:
            print(f"div.field-items не найден на {str(url)}")
            continue

        out_path = Path(out_dir) / f"page_{url.path[1:]}.html"
        out_path.write_text(str(field_items), encoding="utf-8")
        print(f"✅ Сохранено в {out_path}")


download_field_items([
    HttpUrl("http://sniprf.ru/sp25-13330-2012"),
    HttpUrl("http://sniprf.ru/sp6-13130-2021"),
])
