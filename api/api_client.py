from typing import Optional

from requests import Session
from requests.auth import HTTPBasicAuth


class APIClient:
    def __init__(self, endpoint: str) -> None:
        self.session = Session()
        self.endpoint = endpoint

    def post(
        self,
        data: dict,
        auth: Optional[HTTPBasicAuth] = None
    ) -> dict[str, dict]:
        response = self.session.request(
            method='POST',
            url=self.endpoint,
            params=data,
            auth=auth
        )
        response_content = {
            'status_code': response.status_code,
            'response_body': response.json()
            }
        return response_content

    def patch(
            self,
            id: int,
            data: dict,
            auth: Optional[HTTPBasicAuth] = None
    ) -> dict[str, dict]:
        url = f'{self.endpoint}/{id}'
        response = self.session.request(
            method='PATCH',
            url=url,
            params=data,
            auth=auth
        )
        response_content = {
            'status_code': response.status_code,
            'response_body': response.json()
        }
        return response_content

    def delete(
            self,
            id: int,
            data: dict,
            auth: Optional[HTTPBasicAuth] = None
    ) -> dict[str, dict]:
        url = f'{self.endpoint}/{id}'
        response = self.session.request(
            method='DELETE',
            url=url,
            params=data,
            auth=auth
        )
        response_content = {
            'status_code': response.status_code,
            'response_body': response.json()
        }
        return response_content
