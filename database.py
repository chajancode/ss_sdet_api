from typing import Optional

from config.db_config import db_settings, create_mysql_connection


class Database():
    """
    Класс, выполняющий запросы к БД.
    Использует менеджер контекста для автоматического открытия и закрытия\
    соединения.
    Поддерживает выборку данных (SELECT) и модифицирующие операции
    (INSERT/UPDATE/DELETE).

    Attributes:
        db_settings (BaseSettings) : Настройки подключения к БД (хост, порт, \
        пользователь, пароль, БД).

    """
    def __init__(self, db_settings):
        """
        Инициализирует объект Database с заданными настройками.

        Args:
            db_settings (BaseSettings) : Объект настроек, содержащий \
            параметры подключения к БД.
        """
        self.db_settings = db_settings

    def select(
                self, query: str, params: Optional[tuple] = None
            ) -> list:
        """
        Выполняет SELECT-запрос и возвращает все строки результата.

        Args:
            query (str) : SQL-запрос.
            params (Optional[tuple]) : Кортеж параметров для подстановки в \
            запрос. По умолчанию None (параметры не используются).

        Returns:
            list : Список кортежей, где каждый кортеж представляет одну строку\
            результата. Если результат пуст, возвращается пустой список.
        """
        with create_mysql_connection(self.db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()

    def execute(self, query: str, params: Optional[tuple] = None):
        """
        Выполняет INSERT, UPDATE или DELETE запрос и фиксирует транзакцию.

        Args:
            query (str): SQL-запрос.
            params (Optional[tuple]): Кортеж параметров для запроса.\
            По умолчанию None.

        Returns:
            int: Количество затронутых строк (rowcount).
        """
        with create_mysql_connection(self.db_settings) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount


db = Database(db_settings)
