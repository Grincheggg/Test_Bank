import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateTransfer:
    def test_create_transfer_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session,
    ):
        """Позитивный тест: перевод 500 между своими счетами (с 3 000 на 1 000)."""
        # Arrange: создаём два счёта и пополняем их начальными суммами
        initial_1 = 3000
        initial_2 = 1000
        transfer_amount = 500

        account_1 = api_manager.user_steps.create_account(create_user_request)
        account_2 = api_manager.user_steps.create_account(create_user_request)
        api_manager.user_steps.create_deposit(create_user_request, account_1.id, initial_1)
        api_manager.user_steps.create_deposit(create_user_request, account_2.id, initial_2)

        # Act: выполняем перевод с первого счёта на второй
        response = api_manager.user_steps.create_transfer(
            create_user_request,
            account_1.id,
            account_2.id,
            transfer_amount,
        )

        # Получаем актуальное состояние обоих счетов из API и БД
        actual_account_1_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account_1.id,
        )
        actual_account_2_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account_2.id,
        )
        account_1_from_db = Account.get_account_by_id(db_session, account_1.id)
        account_2_from_db = Account.get_account_by_id(db_session, account_2.id)

        # Assert: проверяем ответ API, обновлённые балансы в API и в БД
        assert response.from_account_id == account_1.id
        assert response.to_account_id == account_2.id
        assert actual_account_1_state.balance == initial_1 - transfer_amount
        assert actual_account_2_state.balance == initial_2 + transfer_amount
        assert account_1_from_db is not None, f'Счёт {account_1.id} не найден в БД'
        assert account_2_from_db is not None, f'Счёт {account_2.id} не найден в БД'
        assert account_1_from_db.balance == initial_1 - transfer_amount
        assert account_2_from_db.balance == initial_2 + transfer_amount

    def test_create_transfer_invalid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session,
    ):
        """Негативный тест: попытка перевести 499 (ниже минимума 500), балансы не меняются."""
        # Arrange: создаём два счёта и пополняем их начальными суммами
        initial_1 = 3000
        initial_2 = 1000
        transfer_amount = 499

        account_1 = api_manager.user_steps.create_account(create_user_request)
        account_2 = api_manager.user_steps.create_account(create_user_request)
        api_manager.user_steps.create_deposit(create_user_request, account_1.id, initial_1)
        api_manager.user_steps.create_deposit(create_user_request, account_2.id, initial_2)

        # Act: пытаемся перевести сумму ниже лимита и ожидаем отказ
        api_manager.user_steps.create_transfer_invalid(
            create_user_request,
            account_1.id,
            account_2.id,
            transfer_amount,
        )

        # Получаем состояние обоих счетов после отказа из API и БД
        actual_account_1_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account_1.id,
        )
        actual_account_2_state = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=account_2.id,
        )
        account_1_from_db = Account.get_account_by_id(db_session, account_1.id)
        account_2_from_db = Account.get_account_by_id(db_session, account_2.id)

        # Assert: убеждаемся, что оба баланса остались прежними в API и в БД
        assert actual_account_1_state.balance == initial_1
        assert actual_account_2_state.balance == initial_2
        assert account_1_from_db is not None, f'Счёт {account_1.id} не найден в БД'
        assert account_2_from_db is not None, f'Счёт {account_2.id} не найден в БД'
        assert account_1_from_db.balance == initial_1
        assert account_2_from_db.balance == initial_2
