from http import HTTPStatus

import requests
from requests import Response

from src.main.api.models.create_deposit_request import CreateDepositRequest
from src.main.api.models.create_deposit_response import CreateDepositResponse
from src.main.api.requests.requester import Requester


class CreateDepositRequester(Requester):
    def post(self, create_deposit_request: CreateDepositRequest) -> CreateDepositResponse | Response:
        url = f'{self.base_url}/account/deposit'
        response = requests.post(
            url=url,
            json=create_deposit_request.model_dump(by_alias=True),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return CreateDepositResponse(**response.json())
        return response
