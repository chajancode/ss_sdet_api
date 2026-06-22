from dao.posts_dao import PostsDao
from models.posts.db_record_model import DBPostData
from models.posts.post_create_and_response_dbc import ExpectedPostModel
from utils.string_utils import to_slug


class PostsRepository:
    """
    Репозиторий постов.

    Работает в терминах домена: принимает и возвращает доменные модели,
    а доступ к БД делегирует PostsDao. Преобразование строки БД в модель —
    внутри репозитория.
    """
    def __init__(self, dao: PostsDao) -> None:
        self.dao = dao

    @staticmethod
    def _row_to_model(row: tuple) -> DBPostData:
        """
        Преобразует строку БД в модель поста.
        """
        title, content, status = row
        return DBPostData(title=title, content=content, status=status)

    def get_by_id(self, post_id: int) -> DBPostData | None:
        """
        Возвращает пост как модель (или None, если не найден).
        """
        row = self.dao.select_by_id(post_id)
        if row is None:
            return None
        return self._row_to_model(row)

    def create(self, post: ExpectedPostModel) -> int:
        """Создаёт пост из модели, возвращает id."""
        params = (
            1, post.content, post.title, post.status,
            to_slug(post.title), 'post'
        )
        post_id = self.dao.insert(params)
        if not isinstance(post_id, int):
            raise ValueError('БД не вернула id')
        return post_id

    def create_many(
            self,
            posts: list[ExpectedPostModel]
    ) -> dict[int, ExpectedPostModel]:
        """
        Создаёт несколько постов, возвращает словарь {id: модель}.
        """
        result = {}
        for post in posts:
            post_id = self.create(post)
            result[post_id] = post

        return result

    def delete(self, post_id: int):
        """
        Удаляет пост по его id.
        """
        self.dao.delete(post_id)

    def delete_many(self, post_ids: list):
        """
        Создаёт несколько постов по списку id.
        """
        for post_id in post_ids:
            self.delete(post_id)
