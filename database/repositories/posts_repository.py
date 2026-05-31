from database.database_session import DatabaseSession
from database.queries.posts_queries import PostsQueries
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from utils.string_utils import to_slug


class PostsRepository:
    def __init__(self, session: DatabaseSession) -> None:
        self.session = session

    def create(self, post: ExpectedPostModel) -> int:
        """
        Создаёт один пост в БД, возвращает id
        """
        query = PostsQueries.INSERT
        params = (
            1, post.content, post.title, post.status,
            to_slug(post.title), 'post'
        )
        result = self.session.execute(query, params)
        if isinstance(result, int):
            return result
        else:
            raise ValueError('БД не вернула id')

    def create_many(
            self,
            posts: list[ExpectedPostModel]
    ) -> dict[int, ExpectedPostModel]:
        """
        Создаёт несколько постов в БД, возвращает список с постами и их id
        """
        result = {}
        for post in posts:
            post_id = self.create(post)
            result[post_id] = post

        return result

    def delete(self, post_id: int):
        """
        Удаляет пост из БД по его id
        """
        query = PostsQueries.DELETE
        self.session.execute(query, (post_id,))

    def delete_many(self, post_ids: list):
        """
        Создаёт несколько постов из БД по списку id
        """
        for post_id in post_ids:
            self.delete(post_id)
