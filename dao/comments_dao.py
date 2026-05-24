from dao.base_dao import BaseDao


class CommentsDao(BaseDao):

    def get_comment_by_id(self, id: int) -> list[tuple | None]:
        query = """
            SELECT comment_post_id, comment_content FROM wp_comments
            WHERE comment_id = %s
        """
        result = self.db.select(query, (id,))
        return result
