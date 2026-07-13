import pytest
import allure

from utils.string_utils import to_slug, strip_html

pytestmark = [
    allure.epic('Unit-тесты фреймворка'),
    allure.feature('Утилиты'),
]


@pytest.mark.parametrize(
    'title, expected', [
        ("Hello World", "hello-world"),
        ("Hello, World!", "hello-world"),
        ("Multiple   Spaces", "multiple-spaces"),
        ("", "")
    ]
)
def test_to_slug(title, expected):
    assert to_slug(title) == expected


@pytest.mark.parametrize("html_text, expected", [
    ("<p>text</p>", "text"),
    ("<b>a</b> <i>b</i>", "a b"),
    ("come on", "come on"),
    ("<p>what    if   spaces </p>", "what if spaces"),
    ("<div><span>span</span></div>", "span"),
])
def test_strip_html(html_text, expected):
    assert strip_html(html_text) == expected
