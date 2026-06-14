from services.yandex_service import YandexService
from utils.file_tools import create_text_file, remove_text_file


class TestUploadCopyDownloadFile:

    def test_upload_and_copy_file(
            self,
            yandex_service: YandexService
    ):
        filename = 'data.txt'
        input_folder = 'input_folder'
        output_folder = 'output_folder'
        input_file_path = f'{input_folder}/{filename}'
        output_file_path = f'{output_folder}/{filename}'

        yandex_service.delete_folder_if_exists(input_folder)
        yandex_service.delete_folder_if_exists(output_folder)

        yandex_service.create_folder(params={'path': input_folder})
        yandex_service.create_folder(params={'path': output_folder})

        create_text_file(filename)

        upload_link = yandex_service.request_upload_link(
            {'path': input_file_path}
        )
        assert upload_link.status_code == 200
        assert upload_link.response_body is not None

        upload_result = yandex_service.upload_file(
            filename, upload_link.response_body.href
        )
        assert upload_result.status_code == 201

        copy_result = yandex_service.copy_file(
            input_file_path, output_file_path
        )
        assert copy_result.status_code == 201

        copied_file = yandex_service.get_file_by_path(output_file_path)
        assert copied_file.status_code == 200
        assert copied_file.response_body is not None
        assert copied_file.response_body.name
        assert copied_file.response_body.mime_type
        assert copied_file.response_body.media_type

        repeat_copy_result = yandex_service.copy_file(
            input_file_path, output_file_path
        )
        assert repeat_copy_result.status_code == 409
        assert repeat_copy_result.error is not None
        assert repeat_copy_result.error.error
        assert repeat_copy_result.error.description
        assert repeat_copy_result.error.message

        yandex_service.delete_folder_if_exists(input_folder)
        yandex_service.delete_folder_if_exists(output_folder)
        remove_text_file(filename)

    def test_download_file(
            self,
            yandex_service: YandexService
    ):
        filename = 'data.txt'
        downloaded_filename = 'data_downloaded.txt'
        yandex_disk_folder = 'sdet_data'
        upload_file_path = {'path': f'{yandex_disk_folder}/{filename}'}

        yandex_service.delete_folder_if_exists(yandex_disk_folder)
        create_text_file(filename)
        yandex_service.create_folder(params={'path': yandex_disk_folder})

        upload_link = yandex_service.request_upload_link(
            params=upload_file_path
        )
        assert upload_link.response_body
        upload_result = yandex_service.upload_file(
            filename, upload_link.response_body.href
        )
        assert upload_result.status_code == 201

        download_link = yandex_service.request_download_link(upload_file_path)
        assert download_link.status_code == 200
        assert download_link.response_body

        yandex_service.download_file(
            download_link.response_body.href,
            downloaded_filename
        )
        are_equal, message = yandex_service.compare_files(
            filename, downloaded_filename
        )
        assert are_equal, message

        yandex_service.delete_folder_if_exists(yandex_disk_folder)
        remove_text_file(filename)
        remove_text_file(downloaded_filename)
