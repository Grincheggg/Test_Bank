from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from src.main.api.models.account_transactions_response import AccountTransactionResponse
from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_credit_request import CreateCreditRequest
from src.main.api.models.create_credit_response import CreateCreditResponse
from src.main.api.models.create_deposit_request import CreateDepositRequest
from src.main.api.models.create_deposit_response import CreateDepositResponse
from src.main.api.models.create_repay_request import CreateRepayRequest
from src.main.api.models.create_repay_response import CreateRepayResponse
from src.main.api.models.create_transfer_request import CreateTransferRequest
from src.main.api.models.create_transfer_response import CreateTransferResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.credit_history_response import CreditHistoryResponse
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse


@dataclass
class EndpointConfiguration:
    url: str
    request_model: Optional[Type[BaseModel]]
    response_model: Optional[Type[BaseModel]]


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfiguration(
        url='/admin/create',
        request_model=CreateUserRequest,
        response_model=CreateUserResponse
    )

    ADMIN_DELETE_USER = EndpointConfiguration(
        url='/admin/users',
        request_model=None,
        response_model=None
    )

    LOGIN_USER = EndpointConfiguration(
        url='/auth/token/login',
        request_model=LoginUserRequest,
        response_model=LoginUserResponse
    )

    CREATE_ACCOUNT = EndpointConfiguration(
        url='/account/create',
        request_model=None,
        response_model=CreateAccountResponse
    )

    CREATE_DEPOSIT = EndpointConfiguration(
        url='/account/deposit',
        request_model=CreateDepositRequest,
        response_model=CreateDepositResponse
    )

    CREATE_TRANSFER = EndpointConfiguration(
        url='/account/transfer',
        request_model=CreateTransferRequest,
        response_model=CreateTransferResponse
    )

    CREATE_CREDIT_REQUEST = EndpointConfiguration(
        url='/credit/request',
        request_model=CreateCreditRequest,
        response_model=CreateCreditResponse
    )

    CREATE_CREDIT_REPAY = EndpointConfiguration(
        url='/credit/repay',
        request_model=CreateRepayRequest,
        response_model=CreateRepayResponse
    )

    GET_TRANSACTIONS = EndpointConfiguration(
        url='/account/transactions',
        request_model=None,
        response_model=AccountTransactionResponse
    )

    GET_CREDIT_HISTORY = EndpointConfiguration(
        url='/credit/history',
        request_model=None,
        response_model=CreditHistoryResponse
    )
