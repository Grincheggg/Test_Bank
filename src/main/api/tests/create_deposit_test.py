import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateDeposit:
    def test_create_deposit_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session,
    ):
        """Позитивный тест: пополнение счёта на минимально допустимую сумму 1 000."""
        # Arrange: создаём счёт с нулевым балансом
        deposit_amount = 1000
        account = api_manager.user_steps.create_account(create_user_request)

        # Act: пополняем счёт на 1 000
        response = api_manager.user_steps.create_deposit(
            create_user_request=create_user_request,
            account_id=account.id,
            amount=deposit_amount,
        )

        # Получаем состояние счёта через GET API и напрямую из БД
        actual_account_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, account.id)

        # Assert: сверяем ответ операции, выписку API и данные в БД
        assert response.id == account.id
        assert response.balance == deposit_amount
        assert actual_account_state.balance == deposit_amount
        assert account_from_db is not None, f'Счёт {account.id} не найден в БД'
        assert account_from_db.balance == deposit_amount

    def test_create_deposit_invalid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session,
    ):
        """Негативный тест: попытка пополнить счёт на 999 (ниже лимита 1 000–9 000)."""
        # Arrange: создаём счёт с нулевым балансом
        deposit_amount = 999
        account = api_manager.user_steps.create_account(create_user_request)

        # Act: отправляем невалидную сумму и ожидаем отказ
        api_manager.user_steps.create_deposit_invalid(
            create_user_request=create_user_request,
            account_id=account.id,
            amount=deposit_amount,
        )

        # Получаем состояние счёта через GET API и напрямую из БД
        actual_account_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, account.id)

        # Assert: убеждаемся, что баланс остался 0 в API и в БД
        assert actual_account_state.balance == 0
        assert account_from_db is not None, f'Счёт {account.id} не найден в БД'
        assert account_from_db.balance == 0
