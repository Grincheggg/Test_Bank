from http import HTTPStatus

import requests
from requests import Response

from src.main.api.models.create_repay_request import CreateRepayRequest
from src.main.api.models.create_repay_response import CreateRepayResponse
from src.main.api.requests.requester import Requester


class CreateRepayRequester(Requester):
    def post(self, create_repay_request: CreateRepayRequest) -> CreateRepayResponse | Response:
        url = f'{self.base_url}/credit/repay'
        response = requests.post(
            url=url,
            json=create_repay_request.model_dump(by_alias=True),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return CreateRepayResponse(**response.json())
        return response
