from http import HTTPStatus

import requests
from requests import Response

from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_credit_response import CreateCreditResponse
from src.main.api.requests.requester import Requester


class CreateCreditRequester(Requester):
    def post(self, create_credit_request: CreateCreditRequest) -> CreateCreditResponse | Response:
        url = f'{self.base_url}/credit/request'
        response = requests.post(
            url=url,
            json=create_credit_request.model_dump(by_alias=True),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code == HTTPStatus.CREATED:
            return CreateCreditResponse(**response.json())
        return response
