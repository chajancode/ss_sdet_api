from dataclasses import dataclass

from utils.data_extraction import extract_deleted_folder_path_from_trash


@dataclass
class _Item:
    name: str
    path: str


@dataclass
class _Embedded:
    items: list


@dataclass
class _Trash:
    embedded: object


def test_returns_path_without_trash_prefix():
    trash = _Trash(_Embedded([_Item(name="myfolder", path="trash:/myfolder")]))
    result = extract_deleted_folder_path_from_trash(
                            trash, "myfolder")  # type: ignore
    assert result == "myfolder"


def test_picks_matching_item_among_many():
    trash = _Trash(_Embedded([
        _Item(name="other", path="trash:/other"),
        _Item(name="target", path="trash:/target"),
    ]))
    assert extract_deleted_folder_path_from_trash(
                            trash, "target") == "target"  # type: ignore


def test_not_found_returns_false():
    trash = _Trash(_Embedded([_Item(name="other", path="trash:/other")]))
    assert extract_deleted_folder_path_from_trash(
                            trash, "missing") is False  # type: ignore


def test_empty_items_returns_false():
    trash = _Trash(_Embedded([]))
    assert extract_deleted_folder_path_from_trash(
                            trash, "any") is False  # type: ignore


def test_none_embedded_returns_false():
    trash = _Trash(None)
    assert extract_deleted_folder_path_from_trash(
                            trash, "any") is False  # type: ignore
