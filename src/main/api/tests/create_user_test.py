import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.user_crud import UserCrudDB as User
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateUser:
    # Возможно логичнее убрать здесь parametrize, и сделать генерацию в теле теста?
    @pytest.mark.parametrize(
        'create_user_request',
        [RandomModelGenerator.generate(CreateUserRequest)],
    )
    def test_create_user_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
        db_session: Session,
    ):
        """Позитивный тест: создание пользователя с валидными данными и проверка в БД."""
        # Act: создаём пользователя через API
        response = api_manager.admin_steps.create_user(create_user_request)

        # Получаем пользователя из БД
        user_from_db = User.get_user_by_username(db_session, create_user_request.username)

        # Assert: проверяем ответ API и запись в БД
        assert response.username == create_user_request.username, 'Ошибка, неверный логин'
        assert response.role == create_user_request.role, "Роль не юзер"
        assert user_from_db is not None, f'Пользователь {create_user_request.username} не найден в БД'
        assert user_from_db.username == create_user_request.username, 'Ошибка, неверный логин'

    @pytest.mark.parametrize(
        'username, password',
        [
            ('abи', 'Pas!sw0rd'),               # логин: не латиница
            ('ab', 'Pas!sw0rd'),                # логин: 2 символа (меньше минимума)
            ('abcdefghijklmnpo', 'Pas!sw0rd'),  # логин: 16 символов (больше максимума)
            ('abс!', 'Pas!sw0rd'),              # логин: недопустимый спецсимвол
            ('ab с', 'Pas!sw0rd'),              # логин: пробел
            ('abc', 'Pas!sw0rд'),               # пароль: не латиница
            ('abc', 'Pas!sw0'),                 # пароль: 7 символов (меньше минимума)
            ('abc', 'pas!sw0rd'),               # пароль: без заглавной буквы
            ('abc', 'PAS!SW0RD'),               # пароль: без строчной буквы
            ('abc', 'Passsw0rd'),               # пароль: без спецсимвола
            ('abc', 'Pas!sword'),               # пароль: без цифры
        ],
    )
    def test_create_user_invalid(
        self,
        username: str,
        password: str,
        api_manager: ApiManager,
        db_session: Session,
    ):
        """Негативный тест: попытка создать пользователя с невалидным логином или паролем."""
        # Arrange: формируем запрос с невалидными данными
        create_user_request = CreateUserRequest(
            username=username,
            password=password,
            role='ROLE_USER',
        )

        # Act: отправляем запрос и ожидаем ошибку валидации
        api_manager.admin_steps.create_invalid_user(create_user_request)

        # Assert: убеждаемся, что пользователь не был создан в БД
        user_from_db = User.get_user_by_username(db_session, username)
        assert user_from_db is None, "Создан пользователь с невалидными данными"
