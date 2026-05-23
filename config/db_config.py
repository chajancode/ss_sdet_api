from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
import mysql.connector
from mysql.connector.errors import ConnectionTimeoutError


class DBSettings(BaseSettings):
    DB_NAME: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    @property
    def DB_URL(self) -> str:
        return f'{self.DB_HOST}:{self.DB_PORT}'

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


db_settings = DBSettings()


def create_mysql_connection(db_settings: DBSettings):
    """
    Создаёт подключение к MySQL с использованием настроек из Pydantic.

    Args:
        db_settings(BaseSettings): экземпляр класса pydantic-settings
        BaseSettings
    """
    try:
        connection = mysql.connector.connect(
            host=db_settings.DB_HOST,
            port=db_settings.DB_PORT,
            user=db_settings.DB_USER,
            password=db_settings.DB_PASSWORD,
            database=db_settings.DB_NAME
        )
        return connection
    except Exception as e:
        raise ConnectionTimeoutError(f'Не удалось подключиться к БД: {e}')
