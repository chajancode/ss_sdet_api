import allure

from services.yandex_service import YandexService
from tests.test_yandex.assertions.assertions import (
                                    YandexError,
                                    assert_api_error,
                                    assert_success_link
                                )
from utils.data_generators import GenerateRandomTexts


@allure.epic('Yandex.Disk API')
@allure.feature('Управление папками')
class TestRestoreFolder:
    @allure.story('Восстановление папки из корзины')
    @allure.severity(allure.severity_level.NORMAL)
    def test_restore_folder_from_trash(
            self,
            yandex_service: YandexService
    ):
        params = {'path': GenerateRandomTexts.generate_word()}
        yandex_service.create_folder(params=params)
        yandex_service.delete_folder(params=params)

        result = yandex_service.restore_deleted_folder(params=params)
        assert_success_link(result, 201)

    @allure.story('Восстановление несуществующей папки')
    @allure.severity(allure.severity_level.MINOR)
    def test_restore_folder_doesnt_exist(
            self,
            yandex_service: YandexService
    ):
        params = yandex_service.get_folder_name_doesnt_exist()

        result = yandex_service.restore_folder_doesnt_exist(params=params)
        assert_api_error(result, 404, YandexError.NOT_FOUND)
