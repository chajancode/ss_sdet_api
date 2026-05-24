from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

from api.api_client import APIClient
from dao.base_dao import BaseDao


M = TypeVar('M', bound=BaseModel)
D = TypeVar('D', bound=BaseDao)


class BaseService(Generic[D]):
    def __init__(
                self,
                auth_data: dict,
                endpoint: str,
                dao: D
            ) -> None:
        self.auth = HTTPBasicAuth(**auth_data)
        self.client = APIClient(endpoint, self.auth)
        self._last_created_id = None
        self.dao = dao

    def create(self, test_data, response_model: Type[M]):
        response = self.client.post(test_data, response_model)

        if response.status_code == 201:
            self._last_created_id = response.response_body.id  # type: ignore
        return response

    def patch(self, id, test_data, response_model: Type[M]):
        return self.client.patch(id, test_data, response_model)

    def delete(self, id, test_data, response_model: Type[M]):
        return self.client.delete(id, test_data, response_model)
