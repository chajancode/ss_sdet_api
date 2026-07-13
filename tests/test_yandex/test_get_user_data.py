import allure

from services.yandex_service import YandexService
from tests.test_yandex.assertions.assertions import (
                                    YandexError,
                                    assert_api_error
                                )


@allure.epic('Yandex.Disk API')
@allure.feature('Авторизация')
class TestGetUserData:
    @allure.story('Авторизация с валидным токеном')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_authorize_with_valid_token(
            self, yandex_service: YandexService):
        result = yandex_service.get_authorized_user()
        assert result.status_code == 200
        assert result.response_body is not None
        assert result.response_body.user
        assert result.response_body.user.login
        assert result.response_body.user.display_name

    @allure.story('Авторизация без токена')
    @allure.severity(allure.severity_level.NORMAL)
    def test_authorize_without_token(
            self, yandex_service: YandexService):
        result = yandex_service.get_unauthorized_user()
        assert_api_error(result, 401, YandexError.UNAUTHORIZED)
