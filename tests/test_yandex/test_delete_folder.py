import time

from services.yandex_service import YandexService
from utils.data_generators import GenerateRandomTexts


class TestDeleteFolder:
    def test_delete_folder(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        yandex_service.create_folder(params=params)

        result = yandex_service.delete_folder(params=params)
        assert result.status_code == 204

        time.sleep(2)
        folder_in_storage = yandex_service.folder_in_storage(params=params)
        assert folder_in_storage.status_code == 404

        folder_in_trash = yandex_service.is_folder_in_trash(params=params)
        assert folder_in_trash

    def test_delete_permanently(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}

        yandex_service.create_folder(params=params)

        result = yandex_service.delete_folder(params=params, permanently=True)
        assert result.status_code == 204

        folder_in_storage = yandex_service.folder_in_storage(params=params)
        assert folder_in_storage.status_code == 404

        folder_in_trash = yandex_service.is_folder_in_trash(params=params)
        assert not folder_in_trash

    def test_delete_folder_doesnt_exist(
            self,
            yandex_service: YandexService
    ):
        params = yandex_service.get_folder_name_doesnt_exist()

        result = yandex_service.delete_folder(params=params)
        assert result.status_code == 404
        assert result.error is not None
        assert result.error.error == 'DiskNotFoundError'

    def test_delete_folder_without_params(
            self,
            yandex_service: YandexService
    ):

        result = yandex_service.delete_folder()
        assert result.status_code == 400
        assert result.error is not None
        assert result.error.error == 'FieldValidationError'
