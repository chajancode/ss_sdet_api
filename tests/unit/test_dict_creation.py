from dataclasses import dataclass

from utils.dict_creation import group_by_status


@dataclass
class _Item:
    status: str


def test_group_by_status_mixed():
    ids = [1, 2, 3, 4]
    items = [
        _Item('publish'), _Item('draft'),
        _Item('publish'), _Item('draft')
    ]

    result = group_by_status(ids, items)  # type: ignore

    assert set(result.keys()) == {'publish', 'draft'}
    assert result['publish'] == {1: items[0], 3: items[2]}
    assert result['draft'] == {2: items[1], 4: items[3]}


def test_group_by_status_single_group():
    ids = [5, 6]
    items = [_Item('approved'), _Item('approved')]

    result = group_by_status(ids, items)  # type: ignore

    assert result == {'approved': {5: items[0], 6: items[1]}}


def test_group_by_status_empty():
    result = group_by_status([], [])
    assert result == {}
