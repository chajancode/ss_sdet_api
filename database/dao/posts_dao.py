from typing import Any

from mysql.connector.types import RowItemType, RowType

from database.database_session import DatabaseSession
from database.queries.posts_queries import PostsQueries


class PostsDao:
    """
    DAO для работы с таблицей постов wp_posts.

    Предоставляет методы для работы с постами.
    """
    def __init__(self, session: DatabaseSession) -> None:
        self.session = session

    def select_by_id(
            self, post_id: int
    ) -> (list[RowType | dict[str, RowItemType]] | Any):

        """Возвращает строку поста(или None, если пост не найден)"""
        rows = self.session.select(PostsQueries.SELECT_BY_ID, (post_id,))
        return rows[0] if rows else None  # type: ignore

    def insert(self, params: tuple) -> int | Any | None:
        """Вставляет пост по набору параметров, возвращает id."""
        return self.session.execute(PostsQueries.INSERT, params)

    def delete(self, post_id: int) -> None:
        """Удаляет пост по id."""
        self.session.execute(PostsQueries.DELETE, (post_id,))
