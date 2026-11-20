import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_credit_user_request import CreateCreditUserRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.data.bank_data import MIN_CREDIT, MIN_TERM_MONTHS
from src.main.api.db.crud.credit_crud import CreditCrudDB as Credit


@pytest.mark.api
class TestCreditRequest:
    def test_credit_request_valid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateCreditUserRequest,
        create_credit_account,
        db_session: Session,
    ):
        """Позитивный тест: пользователь с ролью ROLE_CREDIT_SECRET запрашивает кредит на 5 000."""

        # Act: отправляем заявку на кредит
        response = api_manager.user_steps.create_credit_request(
            create_user_request=create_credit_user_request,
            account_id=create_credit_account.id,
            amount=MIN_CREDIT,
            term_months=MIN_TERM_MONTHS,
        )

        # Получаем состояние счёта, историю кредитов и запись счёта из БД
        actual_state_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=create_credit_account.id,
        )
        credit_history = api_manager.user_steps.get_credit_history(create_credit_user_request)
        account_from_db = Account.get_account_by_id(db_session, account_id=create_credit_account.id)

        # Assert: проверяем ответ, историю кредитов, баланс счёта в API и в БД
        assert response.account_id == create_credit_account.id, f'Кредит выдан на другой счет, ожидали:{create_credit_account.id}, получили:{response.account_id} '
        assert response.amount == MIN_CREDIT, f'Запрошенная сумма отличается от фактически выданной, ожидали:{MIN_CREDIT}, получили: {response.amount}'
        assert len(credit_history.credits) == 1, f'Кредит не записался в кредитную историю пользователя'
        assert credit_history.credits[0].credit_id == response.credit_id, f'Id кредита в истории и в ответе не совпадают, ожидали: {response.credit_id} , получили: {credit_history.credits[0].credit_id}'
        assert account_from_db is not None, f'Счёт {create_credit_account.id} не найден в БД'
        assert account_from_db.balance == MIN_CREDIT, f'В БД неверная сумма полученного кредита, ожидали: {MIN_CREDIT} , получили: {account_from_db.balance}'
        assert actual_state_account.balance == MIN_CREDIT, f'Актуальный баланс отличается от суммы запрошенного кредита, ожидали:{MIN_CREDIT} , получили: {actual_state_account.balance}'

    def test_credit_request_invalid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        create_user_account,
        db_session: Session,
    ):
        """Негативный тест: обычный пользователь (ROLE_USER) не может взять кредит."""
        # Act: пытаемся запросить кредит (ожидаем отказ)
        api_manager.user_steps.create_credit_request_invalid(
            create_user_request,
            create_user_account.id,
            amount=MIN_CREDIT,
            term_months=MIN_TERM_MONTHS,
        )

        # Бэкенд запрещает ROLE_USER доступ к истории кредитов
        api_manager.user_steps.get_credit_history_invalid(create_user_request=create_user_request)

        # Получаем состояние счёта через API и БД
        actual_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_user_request,
            account_id=create_user_account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, account_id=create_user_account.id)
        credits_in_db = Credit.get_credits_by_account_id(db_session, account_id=create_user_account.id)

        # Assert: убеждаемся, что деньги  не зачислились на счет ни в API, ни в БД
        assert actual_account.balance == 0, f'Кредит зачислили на счет, должен быть 0, получили: {actual_account.balance}'
        assert account_from_db is not None, f'Счёт {create_user_account.id} не найден в БД'
        assert account_from_db.balance == 0, f'Кредит зачислили на счет, должен быть 0, получили: {account_from_db.balance}'
        assert credits_in_db == [], f' В кредитной истории появился кредит, ожидали пустой список'
