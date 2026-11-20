import allure
from requests import Response

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_deposit_request import CreateDepositRequest
from src.main.api.models.create_repay_request import CreateRepayRequest
from src.main.api.models.create_transfer_request import CreateTransferRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):

    def login_user(self, login_user_request: LoginUserRequest):
        with allure.step(f"Авторизация пользователя {login_user_request.username}"):
            response = ValidateCrudRequester(
                RequestSpecs.base_headers(),
                Endpoint.LOGIN_USER,
                ResponseSpecs.request_ok()
            ).post(login_user_request)
            return response

    def login_user_invalid(self, login_user_request: LoginUserRequest):
        with allure.step(
            f"Попытка авторизации пользователя {login_user_request.username} с невалидными данными"
        ):
            CrudRequester(
                RequestSpecs.base_headers(),
                Endpoint.LOGIN_USER,
                ResponseSpecs.request_bad_unauthorized()
            ).post(login_user_request)

    def create_account(self, create_user_request: CreateUserRequest):
        with allure.step(f"Пользователь {create_user_request.username} открывает новый счет"):
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_ACCOUNT,
                ResponseSpecs.request_created()
            ).post()
            return response

    def create_account_invalid(self):
        with allure.step("Попытка открытия нового счета администратором (ожидается запрет)"):
            response = CrudRequester(
                RequestSpecs.auth_headers(username="admin", password="123456"),
                Endpoint.CREATE_ACCOUNT,
                ResponseSpecs.request_bad_forbidden()
            ).post()
            return response

    def create_deposit(self, create_user_request: CreateUserRequest, account_id: int, amount: float):
        with allure.step(f"Пополнение счета {account_id} на сумму {amount}"):
            create_deposit_request = CreateDepositRequest(accountId=account_id, amount=amount)
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_DEPOSIT,
                ResponseSpecs.request_ok()
            ).post(create_deposit_request)
            return response

    def create_deposit_invalid(self, create_user_request: CreateUserRequest, account_id: int, amount: float):
        with allure.step(f"Попытка пополнения счета {account_id} на невалидную сумму {amount}"):
            create_deposit_request = CreateDepositRequest(accountId=account_id, amount=amount)
            response = CrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_DEPOSIT,
                ResponseSpecs.request_bad()
            ).post(create_deposit_request)
            return response

    def create_transfer(
        self,
        create_user_request: CreateUserRequest,
        from_account_id: int,
        to_account_id: int,
        amount: float,
    ):
        with allure.step(f"Перевод {amount} со счета {from_account_id} на счет {to_account_id}"):
            create_transfer_request = CreateTransferRequest(
                fromAccountId=from_account_id,
                toAccountId=to_account_id,
                amount=amount,
            )
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_TRANSFER,
                ResponseSpecs.request_ok()
            ).post(create_transfer_request)
            return response

    def create_transfer_invalid(
        self,
        create_user_request: CreateUserRequest,
        from_account_id: int,
        to_account_id: int,
        amount: float,
    ):
        with allure.step(
            f"Попытка перевода невалидной суммы {amount} "
            f"со счета {from_account_id} на счет {to_account_id}"
        ):
            create_transfer_request = CreateTransferRequest(
                fromAccountId=from_account_id,
                toAccountId=to_account_id,
                amount=amount,
            )
            response = CrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_TRANSFER,
                ResponseSpecs.request_bad()
            ).post(create_transfer_request)
            return response

    def create_credit_request(
        self,
        create_user_request: CreateUserRequest,
        account_id: int,
        amount: float,
        term_months: int,
    ) -> BaseModel:
        with allure.step(
            f"Пользователь {create_user_request.username} запрашивает кредит "
            f"на сумму {amount} на срок {term_months} мес. для счета {account_id}"
        ):
            create_credit_request = CreateCreditRequest(
                accountId=account_id,
                amount=amount,
                termMonths=term_months,
            )
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_CREDIT_REQUEST,
                ResponseSpecs.request_created()
            ).post(create_credit_request)
            return response

    def create_credit_request_invalid(
        self,
        create_user_request: CreateUserRequest,
        account_id: int,
        amount: float,
        term_months: int,
    ) -> BaseModel:
        with allure.step(
            f"Попытка запроса кредита пользователем {create_user_request.username} "
            f"на сумму {amount} на срок {term_months} мес. для счета {account_id} (негативный сценарий)"
        ):
            create_credit_request = CreateCreditRequest(
                accountId=account_id,
                amount=amount,
                termMonths=term_months,
            )
            response = CrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_CREDIT_REQUEST,
                ResponseSpecs.request_bad_forbidden()
            ).post(create_credit_request)
            return response

    def create_repay(
        self,
        create_user_request: CreateUserRequest,
        credit_id: int,
        account_id: int,
        amount: float,
    ):
        with allure.step(
            f"Пользователь {create_user_request.username} погашает кредит {credit_id} "
            f"со счета {account_id} на сумму {amount}"
        ):
            create_repay_request = CreateRepayRequest(
                accountId=account_id,
                amount=amount,
                creditId=credit_id,
            )
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_CREDIT_REPAY,
                ResponseSpecs.request_ok()
            ).post(create_repay_request)
            return response

    def create_repay_invalid(
        self,
        create_user_request: CreateUserRequest,
        credit_id: int,
        account_id: int,
        amount: float,
    ):
        with allure.step(
            f"Попытка невалидного погашения кредита {credit_id} "
            f"со счета {account_id} на сумму {amount}"
        ):
            create_repay_request = CreateRepayRequest(
                accountId=account_id,
                amount=amount,
                creditId=credit_id,
            )
            response = CrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.CREATE_CREDIT_REPAY,
                ResponseSpecs.request_bad_conflict()
            ).post(create_repay_request)
            return response

    def get_account_transactions(self, create_user_request: CreateUserRequest, account_id: int) -> BaseModel:
        with allure.step(
            f"Пользователь {create_user_request.username} "
            f"запрашивает историю транзакций счета {account_id}"
        ):
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.GET_TRANSACTIONS,
                ResponseSpecs.request_ok()
            ).get(account_id)
            return response

    def get_credit_history(self, create_user_request: CreateUserRequest) -> BaseModel:
        with allure.step(f"Пользователь {create_user_request.username} запрашивает кредитную историю"):
            response = ValidateCrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.GET_CREDIT_HISTORY,
                ResponseSpecs.request_ok()
            ).get()
            return response

    def get_credit_history_invalid(self, create_user_request: CreateUserRequest) -> Response:
        with allure.step(
            f"Попытка получения кредитной истории пользователем "
            f"{create_user_request.username} без прав доступа"
        ):
            response = CrudRequester(
                RequestSpecs.auth_headers(
                    username=create_user_request.username,
                    password=create_user_request.password,
                ),
                Endpoint.GET_CREDIT_HISTORY,
                ResponseSpecs.request_bad_forbidden()
            ).get()
            return response
