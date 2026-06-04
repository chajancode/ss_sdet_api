

from services.yandex_service import YandexService


class TestGetUserData:
    def test_authorize_with_valid_token(
            self, yandex_service: YandexService):
        result = yandex_service.get_authorized_user()
        assert result.status_code == 200
        assert result.response_body is not None
        assert result.response_body.user
        assert result.response_body.user.login
        assert result.response_body.user.display_name

    def test_authorize_without_token(
            self, yandex_service: YandexService):
        result = yandex_service.get_unauthorized_user()
        assert result.status_code == 401
        assert result.error is not None
        assert result.error.error
        assert result.error.description
        assert result.error.message
