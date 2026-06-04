from config.api_config import api_settings, yandex_api_settings


class WordPressEndpoints:
    POSTS_ENDPOINT = f'{api_settings.API_URL}/?rest_route=/wp/v2/posts'
    COMMENTS_ENDPOINT = f'{api_settings.API_URL}/?rest_route=/wp/v2/comments'


class YandexEndpoints:
    DISK_ENDPOINT = f'{yandex_api_settings.YA_API_URL}/v1/disk/'
