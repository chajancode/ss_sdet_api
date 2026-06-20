from jsonschema import validate

from schemas.file_list_schema import file_list_schema
from services.yandex_service import YandexService
from utils.file_tools import create_text_file, remove_text_file


class TestGetFilesList:
    def test_get_files_list(
            self, yandex_service: YandexService
    ):
        folder = 'files_list_folder'
        filenames = ['file_1.txt', 'file_2.txt', 'file_3.txt']

        yandex_service.delete_folder_if_exists(folder)
        yandex_service.create_folder(params={'path': folder})
        for name in filenames:
            create_text_file(name)
            yandex_service.upload_file(name, f'{folder}/{name}')

        result = yandex_service.get_files_list(params={'limit': 3})

        assert result.status_code == 200
        assert result.response_body is not None
        validate(
            instance=result.response_body.model_dump(),
            schema=file_list_schema
        )
        assert result.response_body.limit == 3
        assert len(result.response_body.items) == 3

        yandex_service.delete_folder_if_exists(folder)
        for name in filenames:
            remove_text_file(name)
