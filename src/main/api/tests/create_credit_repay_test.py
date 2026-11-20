import pytest
from sqlalchemy.orm import Session

from src.main.api.models.create_credit_response import CreateCreditResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.db.crud.credit_crud import CreditCrudDB as Credit
from src.main.api.models.create_credit_user_request import CreateCreditUserRequest


@pytest.mark.api
class TestCreditRepayRequest:
    def test_credit_repay_valid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateCreditUserRequest,
        create_credit_account: CreateAccountResponse,
        create_credit_request: CreateCreditResponse,
        db_session: Session,
    ):
        """Позитивный тест: полное погашение действующего кредита и проверка обнуления долга."""
        # Arrange: обновляем состояние аккаунта после получения кредита
        actual_state_account_before_repay = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=create_credit_account.id,
        )

        # Act: полностью погашаем кредит
        response = api_manager.user_steps.create_repay(
            create_user_request=create_credit_user_request,
            credit_id=create_credit_request.credit_id,
            account_id=create_credit_account.id,
            amount=create_credit_request.amount,
        )

        # Получаем обновлённый баланс счёта, историю кредитов и запись из БД
        actual_state_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=create_credit_account.id,
        )
        credit_history = api_manager.user_steps.get_credit_history(
            create_user_request=create_credit_user_request,
        )
        account_from_db = Account.get_account_by_id(db_session, create_credit_account.id)
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id=create_credit_request.credit_id)

        # Assert: проверяем списание денег в API и БД, а также закрытие долга в истории
        assert response.credit_id == create_credit_request.credit_id, f'Id кредитов не совпали, ожидали: {create_credit_request.credit_id} , получили {response.credit_id}'
        assert actual_state_account.balance == actual_state_account_before_repay.balance - create_credit_request.amount, \
            f'Баланс после оплаты кредита в АПИ отличается, ожидали: {actual_state_account_before_repay.balance - create_credit_request.amount}, получили: {actual_state_account.balance}'
        assert len(credit_history.credits) == 1, f'В истории кредитов ожидали 1 запись, получили: {len(credit_history.credits)}'
        assert credit_history.credits[0].balance == 0, f'Долг после погашения должен быть 0, получили: {credit_history.credits[0].balance}'
        assert credit_from_db is not None, f'Данные о кредите отсутствуют в БД'
        assert credit_from_db.balance == 0, f'Долг в БД не закрыт, ожидали 0, пришло: {credit_from_db.balance}'
        assert account_from_db.balance == actual_state_account_before_repay.balance - create_credit_request.amount, \
            f'Баланс после оплаты кредита в БД отличается, ожидали: {actual_state_account_before_repay.balance - create_credit_request.amount}, получили: {account_from_db.balance}'

    def test_credit_repay_invalid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateCreditUserRequest,
        create_credit_account: CreateAccountResponse,
        create_repaid_credit: CreateCreditResponse,
        db_session: Session,
    ):
        """Негативный тест: повторное погашение уже закрытого кредита (ожидаем 409 без списания)."""
        account_before_repay = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=create_credit_account.id,
        )

        # Act: пытаемся повторно погасить уже закрытый кредит
        api_manager.user_steps.create_repay_invalid(
            create_user_request=create_credit_user_request,
            credit_id=create_repaid_credit.credit_id,
            account_id=create_credit_account.id,
            amount=create_repaid_credit.amount,
        )

        # Получаем состояние счёта после отказа из API и БД
        account_after_repay = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=create_credit_account.id,
        )
        credit_history = api_manager.user_steps.get_credit_history(
            create_user_request=create_credit_user_request,
        )

        account_from_db = Account.get_account_by_id(db_session, create_credit_account.id)
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id=create_repaid_credit.credit_id)

        assert account_after_repay.balance == account_before_repay.balance, \
            f'Повторное погашение списало деньги: ожидали баланс {account_before_repay.balance}, получили {account_after_repay.balance}'
        assert account_from_db.balance == account_before_repay.balance, \
            f'В БД баланс изменился после отказа: ожидали {account_before_repay.balance}, получили {account_from_db.balance}'
        assert credit_from_db.balance == 0, f'Долг по кредиту {create_repaid_credit.credit_id} снова открылся: ожидали 0, получили {credit_from_db.balance}'
        assert len(credit_history.credits) == 1, f'В истории кредитов появился дубль: ожидали 1 запись, получили {len(credit_history.credits)}'
        assert credit_history.credits[0].balance == 0, f'Долг в истории кредитов снова открылся: ожидали 0, получили {credit_history.credits[0].balance}'
