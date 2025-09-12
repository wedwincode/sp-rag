from bs4 import Tag
from html_to_markdown import convert_to_markdown


def smart_link_converter(*, tag: Tag, text: str, **kwargs) -> str:
    site = "http://sniprf/"
    src = tag.get("src", "")
    if not src.startswith(site):
        return f"![{text}]({site + src})"
    return f"![{text}]({src})"


html = '<img src="https://example.com" />'
markdown = convert_to_markdown(html, custom_converters={"img": smart_link_converter})
print(markdown)
