from services.yandex_service import YandexService
from utils.data_generators import GenerateRandomTexts


class TestCreateFolder:
    def test_create_folder(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        result = yandex_service.create_folder(params=params)

        assert result.status_code == 201
        assert result.response_body is not None
        assert result.response_body.method == 'GET'
        assert result.response_body.href
        assert isinstance(result.response_body.templated, bool)

        yandex_service.delete_folder(permanently=True, params=params)

    def test_create_folder_with_slash(
            self,
            yandex_service: YandexService
    ):
        params = {'path': '/'}
        result = yandex_service.create_folder(params=params)

        assert result.status_code == 409
        assert result.error is not None
        assert result.error.error == 'DiskPathDoesntExistsError'
        assert result.error.description
        assert result.error.message

    def test_create_folder_without_folder_name(
            self,
            yandex_service: YandexService
    ):
        result = yandex_service.create_folder()

        assert result.status_code == 400
        assert result.error is not None
        assert result.error.error == 'FieldValidationError'
        assert result.error.description
        assert result.error.message

    def test_create_folder_with_existing_folder_name(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        yandex_service.create_folder(params=params)
        result = yandex_service.create_folder(params=params)

        assert result.status_code == 409
        assert result.error is not None
        assert result.error.error == 'DiskPathPointsToExistentDirectoryError'
        assert result.error.description
        assert result.error.message

        yandex_service.delete_folder(permanently=True, params=params)
