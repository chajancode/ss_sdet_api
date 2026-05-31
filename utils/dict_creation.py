from typing import TypeVar

from pydantic import BaseModel


M = TypeVar('M', bound=BaseModel)


def group_by_status(
    item_ids: list[int],
    items: list[M]
) -> dict[str, dict[int, M]]:
    """
    Группирует по статусу.

    Args:
        item_ids (list[int]): Список ID (в том же порядке, что и items)
        items (ExpectedModel): Список объектов
    Returns:
        Словарь вида {status: {id: ExpectedModel}}
    """
    result = {}
    for id, item in zip(item_ids, items):
        status = item.status  # type: ignore
        if status not in result:
            result[status] = {}
        result[status][id] = item
    return result
