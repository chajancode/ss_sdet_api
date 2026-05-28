from dao.base_dao import BaseDao


class CommentsDao(BaseDao):
    """
    DAO для работы с таблицей комментариев wp_comments.

    Предоставляет методы для извлечения данных о комментариях.
    """

    def get_comment_by_id(self, id: int) -> list[tuple | None]:
        """
        Возвращает данные комментария по его идентификатору.

        Выполняет SELECT запрос к таблице wp_comments, извлекая
        поля comment_post_id и comment_content для указанного comment_id.

        Args:
            id (int): Идентификатор комментария (comment_id).

        Returns:
            list[tuple | None]: Результат запроса в виде списка кортежей,
                каждый кортеж содержит (comment_post_id, comment_content).
                Если комментарий не найден, возвращается пустой список.
        """
        query = """
            SELECT comment_post_id, comment_content FROM wp_comments
            WHERE comment_id = %s
        """
        result = self.db.select(query, (id,))
        return result
