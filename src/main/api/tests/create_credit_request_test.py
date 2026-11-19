import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_credit_user_request import CreateCreditUserRequest
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreditRequest:
    def test_credit_request_valid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateCreditUserRequest,
        db_session: Session,
    ):
        """Позитивный тест: пользователь с ролью ROLE_CREDIT_SECRET запрашивает кредит на 5 000."""
        # Arrange: открываем счёт для пользователя с правом на кредит
        credit_amount = 5000
        credit_term_months = 12
        account = api_manager.user_steps.create_account(create_credit_user_request)

        # Act: отправляем заявку на кредит
        response = api_manager.user_steps.create_credit_request(
            create_credit_user_request,
            account.id,
            amount=credit_amount,
            term_months=credit_term_months,
        )

        # Получаем состояние счёта, историю кредитов и запись счёта из БД
        actual_state_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=account.id,
        )
        credit_history = api_manager.user_steps.get_credit_history(create_credit_user_request)
        account_from_db = Account.get_account_by_id(db_session, account_id=account.id)

        # Assert: проверяем ответ, историю кредитов, баланс счёта в API и в БД
        assert response.account_id == account.id
        assert response.amount == credit_amount
        assert len(credit_history.credits) == 1
        assert credit_history.credits[0].credit_id == response.credit_id
        assert credit_history.credits[0].account_id == account.id
        assert actual_state_account.balance == credit_amount
        assert account_from_db is not None, f'Счёт {account.id} не найден в БД'
        assert account_from_db.balance == credit_amount

    def test_credit_request_invalid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session,
    ):
        """Негативный тест: обычный пользователь (ROLE_USER) не может взять кредит."""
        # Arrange: открываем счёт обычному пользователю
        credit_amount = 5000
        credit_term_months = 12
        account = api_manager.user_steps.create_account(create_user_request)

        # Act: пытаемся запросить кредит (ожидаем отказ)
        api_manager.user_steps.create_credit_request_invalid(
            create_user_request,
            account.id,
            amount=credit_amount,
            term_months=credit_term_months,
        )

        # Бэкенд запрещает ROLE_USER доступ к истории кредитов
        api_manager.user_steps.get_credit_history_invalid(create_user_request=create_user_request)

        # Получаем состояние счёта через API и БД
        actual_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, account_id=account.id)

        # Assert: убеждаемся, что деньги  не зачислились на счет ни в API, ни в БД
        assert account.balance == 0
        assert actual_account.balance == 0
        assert account_from_db is not None, f'Счёт {account.id} не найден в БД'
        assert account_from_db.balance == 0
