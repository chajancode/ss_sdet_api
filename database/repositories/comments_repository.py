from database.dao.comments_dao import CommentsDao
from models.comments.comms_create_and_response_dbc import ExpectedCommModel
from models.comments.db_record_model import DBCommentData


class CommentsRepository:
    def __init__(self, dao: CommentsDao) -> None:
        self.dao = dao

    @staticmethod
    def _row_to_model(row: tuple) -> DBCommentData:
        """
        Преобразует строку БД в доменную модель комментария.
        """
        post, content = row
        return DBCommentData(post=post, content=content)

    def get_by_id(self, comment_id: int) -> DBCommentData | None:
        """
        Возвращает комментарий как доменную модель (или None).
        """
        row = self.dao.select_by_id(comment_id)
        if row is None:
            return None
        return self._row_to_model(row)  # type: ignore

    def create(
            self,
            comment: ExpectedCommModel,
            author: str,
            user_id: int
    ) -> int:
        """
        Создаёт комментарий из модели, возвращает id.
        """
        params = (
            comment.post_id, author,
            comment.content, comment.status, user_id
        )
        comment_id = self.dao.insert(params)

        if not isinstance(comment_id, int):
            raise ValueError('БД не вернула id')
        return comment_id

    def create_many(
            self,
            comments: list[ExpectedCommModel],
            author: str,
            user_id: int
    ) -> dict[int, ExpectedCommModel]:
        """
        Создаёт несколько комментариев, возвращает словарь {id: модель}.
        """
        result = {}

        for comm in comments:
            comm_id = self.create(comm, author, user_id)
            result[comm_id] = comm

        return result

    def delete(self, comment_id: int):
        """
        Удаляет комментарий по id.
        """
        self.dao.delete(comment_id)

    def delete_many(self, comm_ids: list[int]):
        """
        Удаляет несколько комментариев по списку id.
        """
        for comm_id in comm_ids:
            self.delete(comm_id)
