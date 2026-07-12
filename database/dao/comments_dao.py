from typing import Any

from mysql.connector.types import RowItemType, RowType

from database.database_session import DatabaseSession
from database.queries.comments_queries import CommentsQueries


class CommentsDao:
    """
    DAO для работы с таблицей комментариев wp_comments.

    Предоставляет методы для извлечения данных о комментариях.
    """
    def __init__(self, session: DatabaseSession) -> None:
        self.session = session

    def select_by_id(
            self, comment_id: int
    ) -> list[RowType | dict[str, RowItemType]] | Any:
        """
        Возвращает строку комментария (или None, если комментарий не найден).
        """
        rows = self.session.select(
            CommentsQueries.SELECT_BY_ID, (comment_id,)
        )
        return rows[0] if rows else None

    def insert(self, params: tuple) -> int | Any | None:
        """Вставляет комментарий по набору параметров, возвращает id."""
        return self.session.execute(CommentsQueries.INSERT, params)

    def delete(self, comment_id: int) -> None:
        """Удаляет комментарий по id."""
        self.session.execute(CommentsQueries.DELETE, (comment_id,))
