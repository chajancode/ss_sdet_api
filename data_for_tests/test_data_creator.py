from pydantic import BaseModel

import data_for_tests.wp_test_data as td
import data_for_tests.test_data_models as tdm


test_data: dict[str, tuple] = {
    'post_create': (td.posts_test_data_create, tdm.PostTestDataCreate),
    'post_patch': (td.posts_test_data_patch, tdm.PostTestDataPatch),
    'post_delete': (td.posts_test_data_delete, tdm.PostTestDataDelete),
    'comms_create': (td.comms_test_data_create, tdm.CommsTestDataCreate),
    'comms_patch': (td.comms_test_data_patch, tdm.CommsTestDataPatch),
    'comms_delete': (td.comms_test_data_delete, tdm.CommsTestDataDelete),
}


def data_creator(data_type: str) -> list[BaseModel]:
    data_list, model = test_data[data_type]
    data_set: list[BaseModel] = [model(**item) for item in data_list]
    return data_set
