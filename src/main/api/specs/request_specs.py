import requests

from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse


class RequestSpecs:
    @staticmethod
    def base_headers():
        return {
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

    @staticmethod
    def auth_headers(username, password):
        request = LoginUserRequest(username=username, password=password)
        response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            headers=RequestSpecs.base_headers(),
            json=request.model_dump()
        )
        if response.status_code == 200:
            response_data = LoginUserResponse(**response.json())
            token = response_data.token
            headers = RequestSpecs.base_headers()
            headers['Authorization'] = f'Bearer {token}'
            return headers
        raise Exception('Login failed')

    @staticmethod
    def no_auth():
        return RequestSpecs.base_headers()
