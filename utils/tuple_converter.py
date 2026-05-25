from models.comments.db_record_model import DBCommentData
from models.posts.db_record_model import DBPostData


def tuple_to_post_model(data) -> DBPostData | None:
    if not data:
        return None
    if isinstance(data, (list, tuple)) and len(data) == 1:
        data = data[0]
    if isinstance(data, (list, tuple)) and len(data) >= 3:
        t, c, s = data
        return DBPostData(title=t, content=c, status=s)
    return None


def tuple_to_comm_model(data) -> DBCommentData | None:
    if not data:
        return None
    if isinstance(data, (list, tuple)) and len(data) == 1 and \
            isinstance(data[0], (list, tuple)):
        data = data[0]
    if isinstance(data, (list, tuple)) and len(data) == 2:
        p, c = data
        return DBCommentData(post=p, content=c)
    return None
