from typing import Optional

import allure
import requests
from requests import Response

from src.main.api.configs.config import Config
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.models.base_model import BaseModel


class CrudRequester(HttpRequester):
    def post(self, model: Optional[BaseModel] = None) -> Response:
        body = model.model_dump(by_alias=True) if model is not None else ''

        with allure.step(f"POST {Config.fetch('backendUrl')}{self.endpoint.value.url}"):
            allure.attach(str(body), 'Request body', allure.attachment_type.JSON)

        response = requests.post(
            url=f"{Config.fetch('backendUrl')}{self.endpoint.value.url}",
            headers=self.request_spec,
            json=body
        )

        with allure.step('Response'):
            allure.attach(
                response.text,
                'Response body',
                allure.attachment_type.JSON
            )

        self.response_spec(response)
        return response

    def delete(self, user_id: int) -> Response:
        response = requests.delete(
            url=f"{Config.fetch('backendUrl')}{self.endpoint.value.url}/{user_id}",
            headers=self.request_spec
        )
        self.response_spec(response)
        return response

    def get(self, item_id: Optional[int] = None) -> Response:
        base_url = f"{Config.fetch('backendUrl')}{self.endpoint.value.url}"
        if item_id is not None:
            base_url = f'{base_url}/{item_id}'

        with allure.step(f'GET {base_url}'):
            pass

        response = requests.get(
            url=base_url,
            headers=self.request_spec
        )
        with allure.step('Response'):
            allure.attach(response.text, 'Response body', allure.attachment_type.JSON)

        self.response_spec(response)
        return response
