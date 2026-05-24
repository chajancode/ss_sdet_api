from database import db
from database import Database


class PostsDao:
    def __init__(self, database: Database = db) -> None:
        self.db = database

    def get_post_by_id(self, id: int) -> list[tuple | None]:
        query = """
            SELECT post_title, post_content, post_status FROM wp_posts
            WHERE ID = %s
        """
        result = self.db.select(query, (id,))
        return result
