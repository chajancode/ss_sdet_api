from models.posts.post_create_and_response_dbc import ExpectedPostModel


def group_by_status(
    post_ids: list[int],
    posts: list[ExpectedPostModel]
) -> dict[str, dict[int, ExpectedPostModel]]:
    """
    Группирует по статусу.

    Args:
        post_ids (list[int]): Список ID постов (в том же порядке, что и posts)
        posts (ExpectedPostModel): Список объектов
    Returns:
        Словарь вида {status: {id: ExpectedPostModel}}
    """
    result = {}
    for pid, post in zip(post_ids, posts):
        status = post.status
        if status not in result:
            result[status] = {}
        result[status][pid] = post
    return result
