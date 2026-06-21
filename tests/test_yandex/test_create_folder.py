from services.yandex_service import YandexService
from utils.data_generators import GenerateRandomTexts
from tests.test_yandex.assertions.assertions import (
                                    YandexError,
                                    assert_api_error,
                                    assert_success_link
                                )


class TestCreateFolder:
    def test_create_folder(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        result = yandex_service.create_folder(params=params)

        assert_success_link(result, 201)

        yandex_service.delete_folder(permanently=True, params=params)

    def test_create_folder_with_slash(
            self,
            yandex_service: YandexService
    ):
        params = {'path': '/'}
        result = yandex_service.create_folder(params=params)

        assert_api_error(result, 409, YandexError.PATH_DOESNT_EXIST)

    def test_create_folder_without_folder_name(
            self,
            yandex_service: YandexService
    ):
        result = yandex_service.create_folder()

        assert_api_error(result, 400, YandexError.FIELD_VALIDATION)

    def test_create_folder_with_existing_folder_name(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        yandex_service.create_folder(params=params)
        result = yandex_service.create_folder(params=params)

        assert_api_error(result, 409, YandexError.PATH_EXISTS)

        yandex_service.delete_folder(permanently=True, params=params)
