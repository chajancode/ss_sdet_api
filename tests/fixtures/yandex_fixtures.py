import pytest

from config.credentials import YA_OAUTH_TOKEN
from services.yandex_service import YandexService
from api.endpoints import YandexEndpoints as ye


@pytest.fixture(scope='function')
def yandex_headers():
    token = f'OAuth {YA_OAUTH_TOKEN}'
    return {'Authorization': token}


@pytest.fixture(scope='function')
def yandex_service(yandex_headers):
    return YandexService(ye.DISK_ENDPOINT, headers=yandex_headers)
