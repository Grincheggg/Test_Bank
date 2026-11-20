import pytest

from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_credit_response import CreateCreditResponse
from src.main.api.data.bank_data import MAX_DEPOSIT
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_deposit_request import CreateDepositRequest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_credit_user_request import CreateCreditUserRequest
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture
def create_user_request(api_manager: ApiManager):
    """Создаёт обычного пользователя (ROLE_USER) и возвращает данные запроса."""
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture
def create_credit_user_request(api_manager: ApiManager):
    """Создаёт пользователя с правом на кредит (ROLE_CREDIT_SECRET) и возвращает данные запроса."""
    user_request = RandomModelGenerator.generate(CreateCreditUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture
def create_user_account(api_manager: ApiManager, create_user_request: CreateUserRequest):
    account = api_manager.user_steps.create_account(create_user_request)
    return account


@pytest.fixture
def create_two_accounts(api_manager: ApiManager, create_user_request: CreateUserRequest) -> tuple[CreateAccountResponse, CreateAccountResponse]:
    account_1 = api_manager.user_steps.create_account(create_user_request)
    account_2 = api_manager.user_steps.create_account(create_user_request)
    return account_1, account_2


@pytest.fixture
def create_two_funded_accounts(api_manager: ApiManager, create_user_request: CreateUserRequest, create_two_accounts: tuple[CreateAccountResponse, CreateAccountResponse]):
    account_1, account_2 = create_two_accounts
    prepared_1 = RandomModelGenerator.generate(CreateDepositRequest)
    prepared_2 = RandomModelGenerator.generate(CreateDepositRequest)
    account_dep_1 = api_manager.user_steps.create_deposit(
        create_user_request,
        account_1.id,
        prepared_1.amount,
    )
    account_dep_2 = api_manager.user_steps.create_deposit(
        create_user_request,
        account_2.id,
        prepared_2.amount,
    )
    return account_dep_1, account_dep_2


@pytest.fixture
def create_credit_account(api_manager: ApiManager, create_credit_user_request: CreateCreditUserRequest):
    account = api_manager.user_steps.create_account(create_credit_user_request)
    return account


@pytest.fixture
def create_credit_request(
        api_manager: ApiManager,
        create_credit_user_request: CreateUserRequest,
        create_credit_account: CreateAccountResponse
) -> CreateCreditResponse:
    prepared_credit = RandomModelGenerator.generate(CreateCreditRequest)
    credit = api_manager.user_steps.create_credit_request(
        create_user_request=create_credit_user_request,
        account_id=create_credit_account.id,
        amount=prepared_credit.amount,
        term_months=prepared_credit.term_months
    )
    return credit


@pytest.fixture
def create_repaid_credit(
        api_manager: ApiManager,
        create_credit_user_request: CreateUserRequest,
        create_credit_account: CreateAccountResponse
) -> CreateCreditResponse:
    prepared_credit = RandomModelGenerator.generate(CreateCreditRequest)
    api_manager.user_steps.create_deposit(
        create_user_request=create_credit_user_request,
        account_id=create_credit_account.id,
        amount=MAX_DEPOSIT
    )
    api_manager.user_steps.create_deposit(
        create_user_request=create_credit_user_request,
        account_id=create_credit_account.id,
        amount=MAX_DEPOSIT
    )

    credit = api_manager.user_steps.create_credit_request(
        create_user_request=create_credit_user_request,
        account_id=create_credit_account.id,
        amount=prepared_credit.amount,
        term_months=prepared_credit.term_months
    )
    api_manager.user_steps.create_repay(
        create_user_request=create_credit_user_request,
        credit_id=credit.credit_id,
        account_id=credit.account_id,
        amount=prepared_credit.amount,
    )

    return credit
