import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateAccount:
    def test_create_account_valid(
        self,
        db_session: Session,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
    ):
        """Позитивный тест: создание банковского счёта обычным пользователем."""
        # Act: создаём счёт через API
        response = api_manager.user_steps.create_account(create_user_request)

        # Получаем созданный счёт из БД
        account_from_db = Account.get_account_by_id(db_session, response.id)

        # Assert: проверяем ответ API и наличие записи в БД
        assert response.balance == 0, f'Счет при инициации должен быть равен 0, a равен - {response.balance}'
        assert account_from_db is not None, f'Счёт {response.id} не найден в БД'
        assert account_from_db.id == response.id, 'ID счёта в БД не совпадает с ответом API'
        assert account_from_db.balance == 0, 'Начальный баланс созданного счёта в БД должен быть 0'

    def test_create_account_invalid(self, api_manager: ApiManager):
        """Негативный тест: администратор не может создать себе банковский счёт."""
        # Act & Assert: попытка создать счёт от имени администратора возвращает ошибку
        api_manager.user_steps.create_account_invalid()
