from typing import Optional, Type, TypeVar

from pydantic import BaseModel
from requests import Session
from requests.auth import HTTPBasicAuth

from models.api_responses_models import FullAPIResponse

M = TypeVar('M', bound=BaseModel)


class APIClient:
    def __init__(self, endpoint: str, auth: HTTPBasicAuth) -> None:
        self.session = Session()
        self.endpoint: str = endpoint
        self.auth = auth

    def _request(
                self,
                method: str,
                response_model: Type[M],
                id: Optional[int] = None,
                data: Optional[dict] = None,
    ) -> FullAPIResponse[M]:

        url = f'{self.endpoint}/{id}' if id else self.endpoint

        response = self.session.request(
                method=method,
                url=url,
                json=data,
                auth=self.auth,
        )
        parsed_body = response_model(**response.json())
        return FullAPIResponse[M](
                status_code=response.status_code,
                response_body=parsed_body
        )

    def post(
                self,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M]:

        return self._request(
                method='POST',
                data=data,
                response_model=response_model

        )

    def patch(
                self,
                id: int,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M]:

        return self._request(
                method='PATCH',
                id=id,
                data=data,
                response_model=response_model,
        )

    def delete(
                self,
                id: int,
                data: dict,
                response_model: Type[M]
    ) -> FullAPIResponse[M]:
        return self._request(
                method='DELETE',
                id=id,
                data=data,
                response_model=response_model,
        )
