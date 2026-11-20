import pytest
from sqlalchemy.orm import Session

from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.data.bank_data import MIN_DEPOSIT, LOWER_THAN_MIN_DEP


@pytest.mark.api
class TestCreateDeposit:
    def test_create_deposit_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        create_user_account: CreateAccountResponse,
        db_session: Session,
    ):
        """Позитивный тест: пополнение счёта на минимально допустимую сумму."""

        # Act: пополняем счёт на 1 000(минимальный депозит)
        response = api_manager.user_steps.create_deposit(
            create_user_request=create_user_request,
            account_id=create_user_account.id,
            amount=MIN_DEPOSIT,
        )

        # Получаем состояние счёта через GET API и напрямую из БД
        actual_account_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=create_user_account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, create_user_account.id)

        # Assert: сверяем ответ операции, выписку API и данные в БД
        assert response.id == create_user_account.id, f'В ответ пришел неверный id счета: {response.id}, ожидали {create_user_account.id}'
        assert response.balance == MIN_DEPOSIT, f'Ошибка пополнения, ожидаемый результат после пополнения {MIN_DEPOSIT}, фактический: {response.balance}'
        assert actual_account_state.balance == MIN_DEPOSIT, f'Ошибка пополнения, ожидаемый результат после пополнения {MIN_DEPOSIT}, фактический: {actual_account_state.balance}'
        assert account_from_db is not None, f'Счёт {create_user_account.id} не найден в БД'
        assert account_from_db.balance == actual_account_state.balance, f'Расхождение данных БД и АПИ, в БД: {account_from_db.balance}, в АПИ {actual_account_state.balance}'

    def test_create_deposit_invalid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        create_user_account: CreateAccountResponse,
        db_session: Session,
    ):
        """Негативный тест: попытка пополнить счёт на 999 (ниже лимита 1 000)."""
        # Act: отправляем невалидную сумму и ожидаем отказ
        api_manager.user_steps.create_deposit_invalid(
            create_user_request=create_user_request,
            account_id=create_user_account.id,
            amount=LOWER_THAN_MIN_DEP,
        )

        # Получаем состояние счёта через GET API и напрямую из БД
        actual_account_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=create_user_account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, create_user_account.id)

        # Assert: убеждаемся, что баланс остался 0 в API и в БД
        assert actual_account_state.balance == 0, f'Ожидали, что баланс останется 0 после отказа, получили {account_from_db.balance}'
        assert account_from_db is not None, f'Счёт {create_user_account.id} не найден в БД'
        assert account_from_db.balance == 0, f'Ожидали, что баланс останется 0 после отказа, получили {account_from_db.balance}'
