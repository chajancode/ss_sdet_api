import allure

from utils.yandex_file_manager import YandexFileManager

pytestmark = [
    allure.epic('Unit-тесты фреймворка'),
    allure.feature('Утилиты'),
]


def test_compare_files_equal(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("username=SDET\npassword=secret_key")
    b.write_text("username=SDET\npassword=secret_key")
    equal, message = YandexFileManager.compare_files(str(a), str(b))
    assert equal is True
    assert "Содержимое файлов одинаково" in message


def test_compare_files_different(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("одно содержимое")
    b.write_text("другое содержимое")
    equal, message = YandexFileManager.compare_files(str(a), str(b))
    assert equal is False
    assert "Cодержимое файлов отличается" in message
