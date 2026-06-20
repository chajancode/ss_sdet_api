import pytest

from config.credentials import YA_OAUTH_TOKEN
from services.yandex_service import YandexService


@pytest.fixture(scope='function')
def yandex_headers():
    token = f'OAuth {YA_OAUTH_TOKEN}'
    return {'Authorization': token}


@pytest.fixture(scope='function')
def yandex_service(yandex_headers):
    return YandexService(headers=yandex_headers)
