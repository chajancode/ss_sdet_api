from models.yandex.resource_models import TrashModel


def extract_deleted_folder_path_from_trash(
                    body: TrashModel, name: str) -> str | bool:
    if body.embedded is not None:
        for item in body.embedded.items:
            if item.name == name:
                path = item.path.removeprefix('trash:/')
                return path
    return False
