from services.yandex_service import YandexService
from utils.data_generators import GenerateRandomTexts


class TestRestoreFolder:
    def test_restore_folder_from_trash(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        yandex_service.create_folder(params=params)
        yandex_service.delete_folder(params=params)

        result = yandex_service.restore_deleted_folder(params=params)
        assert result.status_code == 201
        assert result.response_body is not None
        assert result.response_body.method == 'GET'
        assert result.response_body.href
        assert isinstance(result.response_body.templated, bool)

    def test_restore_folder_doesnt_exist(
            self,
            yandex_service: YandexService
    ):
        params = yandex_service.get_folder_name_doesnt_exist()

        result = yandex_service.restore_folder_doesnt_exist(params=params)
        assert result.status_code == 404
        assert result.error is not None
        assert result.error.error == 'DiskNotFoundError'
        assert result.error.description
        assert result.error.message
