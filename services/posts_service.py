from requests.auth import HTTPBasicAuth

from api.endpoints import WordPressEndpoints as wpe
from api.api_client import APIClient


class PostsService:
    def __init__(self, auth_data: dict) -> None:
        self.auth = HTTPBasicAuth(**auth_data)
        self.client = APIClient(wpe.POSTS_ENDPOINT, self.auth)

    def create(self, test_data):
        return self.client.post(test_data)

    def patch(self, id, test_data):
        return self.client.patch(id, test_data)

    def delete(self, id, test_data):
        return self.client.delete(id, test_data)
