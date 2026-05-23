from typing import Any, Optional

from requests import Session
from requests.auth import HTTPBasicAuth


class APIClient:
    def __init__(self, endpoint: str, auth: HTTPBasicAuth) -> None:
        self.session = Session()
        self.endpoint: str = endpoint
        self.auth = auth

    def _request(
            self,
            method: str,
            url: str,
            id: Optional[int] = None,
            data: Optional[dict] = None,
    ) -> dict[str, Any]:
        if id:
            url = f'{self.endpoint}/{id}'

        response = self.session.request(
            method=method,
            url=url,
            json=data,
            auth=self.auth
        )
        return {
            'status_code': response.status_code,
            'response_body': response.json()
        }

    def post(
        self,
        data: dict,
    ) -> dict[str, dict]:

        return self._request(
            method='POST',
            url=self.endpoint,
            data=data
        )

    def patch(
            self,
            id: int,
            data: dict,
    ) -> dict[str, dict]:

        return self._request(
            method='PATCH',
            url=self.endpoint,
            id=id,
            data=data
        )

    def delete(
            self,
            id: int,
            data: dict,
    ) -> dict[str, dict]:
        return self._request(
            method='DELETE',
            url=self.endpoint,
            id=id,
            data=data
        )
