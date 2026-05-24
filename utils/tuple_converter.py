from models.db_record_model import DBPostData


def tuples_to_models(data: list) -> list[DBPostData] | None:
    if data:
        posts_from_db = [
            DBPostData(title=t, content=c, status=s) for (t, c, s) in data
        ]
        return posts_from_db
    return None


def tuple_to_model(data: tuple | None) -> DBPostData | None:
    print(f'!!!!!!!!{data}')
    if data:
        t, c, s = data
        post_from_db = DBPostData(
            title=t,
            content=c,
            status=s
        )
        return post_from_db
    return None
