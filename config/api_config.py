from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    API_HOST: Optional[str] = None
    API_PORT: Optional[str] = None
    API_USER: Optional[str] = None
    API_PSWD: Optional[str] = None

    @property
    def API_URL(self) -> str:
        return f'http://{self.API_HOST}:{self.API_PORT}'

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


api_settings = APISettings()


class YandexAPISettings(BaseSettings):
    YA_OAUTH_TOKEN: Optional[str] = None
    YA_HOST: Optional[str] = None

    @property
    def YA_API_URL(self) -> str:
        return f'{self.YA_HOST}'

    model_config = SettingsConfigDict(
        env_file='.env.yandex', env_file_encoding='utf-8'
    )


yandex_api_settings = YandexAPISettings()
