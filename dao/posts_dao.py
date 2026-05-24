from dao.base_dao import BaseDao


class PostsDao(BaseDao):

    def get_post_by_id(self, id: int) -> list[tuple | None]:
        query = """
            SELECT post_title, post_content, post_status FROM wp_posts
            WHERE ID = %s
        """
        result = self.db.select(query, (id,))
        return result
