from dao.base_dao import BaseDao


class PostsDao(BaseDao):
    """
    DAO для работы с таблицей постов wp_posts.

    Предоставляет методы для извлечения данных о постах.
    """
    def get_post_by_id(self, id: int) -> list[tuple | None]:
        """
        Возвращает данные поста по его идентификатору.

        Выполняет SELECT запрос к таблице wp_posts, извлекая
        поля post_title, post_content, post_status для указанного ID.

        Args:
            id (int): Идентификатор поста (ID).

        Returns:
            list[tuple | None]: Результат запроса в виде списка кортежей,
                каждый кортеж содержит (post_title, post_content, post_status).
                Если пост не найден, возвращается пустой список.
        """
        query = """
            SELECT post_title, post_content, post_status FROM wp_posts
            WHERE ID = %s
        """
        result = self.db.select(query, (id,))
        return result
