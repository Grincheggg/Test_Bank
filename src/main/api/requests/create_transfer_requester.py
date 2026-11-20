from http import HTTPStatus

import requests
from requests import Response

from src.main.api.models.create_transfer_request import CreateTransferRequest
from src.main.api.models.create_transfer_response import CreateTransferResponse
from src.main.api.requests.requester import Requester


class CreateTransferRequester(Requester):
    def post(self, create_transfer_request: CreateTransferRequest) -> CreateTransferResponse | Response:
        url = f'{self.base_url}/account/transfer'
        response = requests.post(
            url=url,
            json=create_transfer_request.model_dump(by_alias=True),
            headers=self.headers
        )
        self.response_spec(response)
        if response.status_code == HTTPStatus.OK:
            return CreateTransferResponse(**response.json())
        return response
