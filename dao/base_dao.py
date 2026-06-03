
from database.database import Database


class BaseDao:
    """
    Базовый DAO для работы с базой данных.

    Предоставляет доступ к экземпляру Database для выполнения запросов.
    Может быть унаследован конкретными DAO для работы с разными таблицами.

    Attributes:
        db (Database): Объект для взаимодействия с БД.
    """
    def __init__(self, database: Database) -> None:
        """
        Инициализирует базовый DAO.

        Args:
            database (Database): Экземпляр Database. По умолчанию \
            используется глобальный объект `db`, импортированный из модуля \
            database.
        """
        self.db = database
