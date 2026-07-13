import logging

from config.db_config import DBSettings, create_mysql_connection


logger = logging.getLogger(__name__)


class DatabaseSession:
    """
    Класс для создания сессии запросов к БД
    """
    def __init__(self, db_settings: DBSettings) -> None:
        self.conn = create_mysql_connection(db_settings)
        self.conn.autocommit = True  # type: ignore

    def execute(self, query: str, params: tuple = ()):
        logger.debug(f'SQL execute: {query.strip()} | params: {params}')
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query, params)
            except Exception as e:
                logger.error(f'Ошибка SQL-запроса: {e} | {query.strip()}')
                raise RuntimeError(f'Ошибка при запросe: {e}') from e
        return cursor.lastrowid

    def select(self, query: str, params: tuple = ()):
        logger.debug(f'SQL select: {query.strip()} | params: {params}')
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            logger.debug(f'Cursor вернул {len(rows)} строк')
            return rows

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()
