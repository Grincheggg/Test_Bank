import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.data.bank_data import MIN_TRANSFER, LOWER_THAN_MIN_TRANSFER


@pytest.mark.api
class TestCreateTransfer:
    def test_create_transfer_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        create_two_funded_accounts,
        db_session: Session,
    ):
        """Позитивный тест: перевод 500(MIN_TRANSFER) между своими счетами."""
        account_1, account_2 = create_two_funded_accounts
        # Act: выполняем перевод с первого счёта на второй
        response = api_manager.user_steps.create_transfer(
            create_user_request,
            account_1.id,
            account_2.id,
            MIN_TRANSFER,
        )
        # Получаем актуальное состояние обоих счетов из БД и АПИ
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
        assert response.from_account_id == account_1.id and response.to_account_id == account_2.id, \
            f'В ответе API неверные счета: ожидали {account_1.id} -> {account_2.id}, получили {response.from_account_id} -> {response.to_account_id}'
        assert account_1_from_db is not None, f'Счёт {account_1.id} не найден в БД'
        assert account_2_from_db is not None, f'Счёт {account_2.id} не найден в БД'
        assert account_1_from_db.balance == account_1.balance - MIN_TRANSFER, f'Неправильно списание средств в БД, ожидали:{account_1.balance - MIN_TRANSFER} , получили: {account_1_from_db.balance}'
        assert account_2_from_db.balance == account_2.balance + MIN_TRANSFER, f'Неправильно зачисление средств в БД, ожидали:{account_2.balance + MIN_TRANSFER} , получили: {account_2_from_db.balance}'
        assert actual_account_1_state.balance == account_1.balance - MIN_TRANSFER, f'Неправильно списание средств вАПИ, ожидали:{account_1.balance - MIN_TRANSFER} , получили: {actual_account_1_state.balance}'
        assert actual_account_2_state.balance == account_2.balance + MIN_TRANSFER, f'Неправильно зачисление средств в АПИ, ожидали:{account_2.balance + MIN_TRANSFER} , получили: {actual_account_2_state.balance}'

    def test_create_transfer_invalid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        create_two_funded_accounts,
        db_session: Session,
    ):
        """Негативный тест: попытка перевести 499 (ниже минимума 500), балансы не меняются."""
        account_1, account_2 = create_two_funded_accounts

        # Act: пытаемся перевести сумму ниже лимита и ожидаем отказ
        api_manager.user_steps.create_transfer_invalid(
            create_user_request,
            account_1.id,
            account_2.id,
            LOWER_THAN_MIN_TRANSFER,
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
        assert actual_account_1_state.balance == account_1.balance, f'Баланс отправителя изменился, ожидался {account_1.balance} , получили{actual_account_1_state.balance}'
        assert actual_account_2_state.balance == account_2.balance, f'Баланс получателя изменился, ожидался {account_2.balance} , получили{actual_account_2_state.balance}'
        assert account_1_from_db.balance == account_1.balance, f'Баланс отправителя изменился, ожидался {account_1.balance} , получили{account_1_from_db.balance}'
        assert account_2_from_db.balance == account_2.balance, f'Баланс получателя изменился, ожидался {account_2.balance} , получили{account_2_from_db.balance}'
