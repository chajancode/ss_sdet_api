from requests.auth import HTTPBasicAuth

from api.endpoints import WordPressEndpoints as wpe
from api.api_client import APIClient


class PostsService:

    def create(self, test_data, auth_data):
        basic_auth = HTTPBasicAuth(**auth_data)
        client = APIClient(wpe.POSTS_ENDPOINT)
        return client.post(test_data, basic_auth)

    def patch(self, id, test_data, auth_data):
        basic_auth = HTTPBasicAuth(**auth_data)
        client = APIClient(wpe.POSTS_ENDPOINT)
        return client.patch(id, test_data, basic_auth)

    def delete(self, id, test_data, auth_data):
        basic_auth = HTTPBasicAuth(**auth_data)
        client = APIClient(wpe.POSTS_ENDPOINT)
        return client.delete(id, test_data, basic_auth)
