import allure

from services.yandex_service import YandexService
from tests.test_yandex.assertions.assertions import (
                                    YandexError,
                                    assert_api_error
                                )
from utils.data_generators import GenerateRandomTexts


@allure.epic('Yandex.Disk API')
@allure.feature('Управление папками')
class TestDeleteFolder:
    @allure.story('Удаление папки (в корзину)')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_folder(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        yandex_service.create_folder(params=params)

        result = yandex_service.delete_folder(params=params)
        assert result.status_code == 204

        folder_in_storage = yandex_service.folder_in_storage(params=params)
        assert folder_in_storage.status_code == 404

        folder_in_trash = yandex_service.is_folder_in_trash(params=params)
        assert folder_in_trash

        yandex_service.empty_trash()

    @allure.story('Удаление папки безвозвратно')
    @allure.severity(allure.severity_level.NORMAL)
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

    @allure.story('Удаление несуществующей папки')
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_folder_doesnt_exist(
            self,
            yandex_service: YandexService
    ):
        params = yandex_service.get_folder_name_doesnt_exist()

        result = yandex_service.delete_folder(params=params)
        assert_api_error(result, 404, YandexError.NOT_FOUND)

    @allure.story('Удаление без параметров')
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_folder_without_params(
            self,
            yandex_service: YandexService
    ):

        result = yandex_service.delete_folder()
        assert_api_error(result, 400, YandexError.FIELD_VALIDATION)
