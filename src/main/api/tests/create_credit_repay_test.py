import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_credit_user_request import CreateCreditUserRequest


@pytest.mark.api
class TestCreditRepayRequest:
    def test_credit_repay_valid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateCreditUserRequest,
        db_session: Session,
    ):
        """Позитивный тест: полное погашение действующего кредита и проверка обнуления долга."""
        # Arrange: создаём счёт, оформляем кредит и фиксируем баланс после выдачи
        credit_amount = 5000
        credit_term_months = 12
        account = api_manager.user_steps.create_account(create_credit_user_request)
        credit = api_manager.user_steps.create_credit_request(
            create_user_request=create_credit_user_request,
            account_id=account.id,
            amount=credit_amount,
            term_months=credit_term_months,
        )
        account_after_credit = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=account.id,
        )

        # Act: полностью погашаем кредит
        response = api_manager.user_steps.create_repay(
            create_user_request=create_credit_user_request,
            credit_id=credit.credit_id,
            account_id=account.id,
            amount=credit_amount,
        )

        # Получаем обновлённый баланс счёта, историю кредитов и запись из БД
        actual_state_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=account.id,
        )
        credit_history = api_manager.user_steps.get_credit_history(
            create_user_request=create_credit_user_request,
        )
        account_from_db = Account.get_account_by_id(db_session, account.id)

        # Assert: проверяем списание денег в API и БД, а также закрытие долга в истории
        assert response.credit_id == credit.credit_id
        assert actual_state_account.balance == account_after_credit.balance - credit_amount
        assert account_from_db is not None, f'Счёт {account.id} не найден в БД'
        assert account_from_db.balance == account_after_credit.balance - credit_amount
        assert len(credit_history.credits) == 1
        assert credit_history.credits[0].balance == 0.0

    def test_credit_repay_invalid(
        self,
        api_manager: ApiManager,
        create_credit_user_request: CreateCreditUserRequest,
        db_session: Session,
    ):
        """Негативный тест: повторное погашение уже закрытого кредита (ожидаем 409 без списания)."""
        # Arrange: создаём счёт, оформляем кредит и полностью его погашаем
        credit_amount = 5000
        cash_for_repeat_repay = 5000
        credit_term_months = 12

        account = api_manager.user_steps.create_account(create_credit_user_request)
        credit = api_manager.user_steps.create_credit_request(
            create_user_request=create_credit_user_request,
            account_id=account.id,
            amount=credit_amount,
            term_months=credit_term_months,
        )
        api_manager.user_steps.create_repay(
            create_user_request=create_credit_user_request,
            credit_id=credit.credit_id,
            account_id=account.id,
            amount=credit_amount,
        )

        # Пополняем счёт перед повторной попыткой, чтобы банк не отказал по 422 (нехватка средств),
        # а дошёл до проверки статуса кредита и вернул 409 Conflict
        api_manager.user_steps.create_deposit(
            create_user_request=create_credit_user_request,
            account_id=account.id,
            amount=cash_for_repeat_repay,
        )

        # Act: пытаемся повторно погасить уже закрытый кредит
        api_manager.user_steps.create_repay_invalid(
            create_user_request=create_credit_user_request,
            credit_id=credit.credit_id,
            account_id=account.id,
            amount=credit_amount,
        )

        # Получаем состояние счёта после отказа из API и БД
        actual_state_account = api_manager.user_steps.get_account_transactions(
            create_user_request=create_credit_user_request,
            account_id=account.id,
        )
        account_from_db = Account.get_account_by_id(db_session, account.id)

        # Assert: убеждаемся, что повторного списания не произошло ни в API, ни в БД
        assert actual_state_account.balance == cash_for_repeat_repay
        assert account_from_db is not None, f'Счёт {account.id} не найден в БД'
        assert account_from_db.balance == cash_for_repeat_repay
