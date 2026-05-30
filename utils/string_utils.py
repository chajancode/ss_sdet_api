import re

from slugify import slugify


def to_slug(title) -> str:
    return slugify(title)


def strip_html(html_text) -> str:
    cleaned = re.sub(r'<[^>]+>', '', html_text)
    cleaned = ' '.join(cleaned.split())
    return cleaned
