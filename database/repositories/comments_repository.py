from database.database_session import DatabaseSession
from database.queries.comments_queries import CommentsQueries
from models.comments.comms_create_and_response_dbc import ExpectedCommModel


class CommentsRepository:
    def __init__(self, session: DatabaseSession) -> None:
        self.session = session

    def create(
            self,
            comment: ExpectedCommModel,
            author: str,
            user_id: int
    ) -> int:
        query = CommentsQueries.INSERT
        params = (
            comment.post_id, author,
            comment.content, comment.status, user_id
        )
        result = self.session.execute(query, params)

        if isinstance(result, int):
            return result
        else:
            raise ValueError('БД не вернула id')

    def create_many(
            self,
            comments: list[ExpectedCommModel],
            author: str,
            user_id: int
    ) -> dict[int, ExpectedCommModel]:

        result = {}

        for comm in comments:
            comm_id = self.create(comm, author, user_id)
            result[comm_id] = comm

        return result

    def delete(self, comm_id: int):
        query = CommentsQueries.DELETE
        self.session.execute(query, (comm_id,))

    def delete_many(self, comm_ids: list[int]):
        for comm_id in comm_ids:
            self.delete(comm_id)
