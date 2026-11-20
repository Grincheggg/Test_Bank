import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.login_user_request import LoginUserRequest


@pytest.mark.api
class TestUserLogin:
    def test_admin_login_valid(self, api_manager: ApiManager):
        """Позитивный тест: успешная авторизация администратора."""
        # Arrange
        login_admin_request = LoginUserRequest(username='admin', password='123456')

        # Act
        response = api_manager.user_steps.login_user(login_admin_request)

        # Assert
        assert response.user.username == login_admin_request.username, \
            f"Не совпал логин при авторизации администратором, пришел {response.user.username} вместо {login_admin_request.username}"
        assert response.user.role == 'ROLE_ADMIN', f"Роль не админ, a {response.user.role}"

    def test_admin_login_invalid(self, api_manager: ApiManager):
        """Негативный тест: авторизация с несуществующим логином администратора."""
        # Arrange
        login_admin_request = LoginUserRequest(username='admin13', password='123456')

        # Act & Assert
        api_manager.user_steps.login_user_invalid(login_admin_request)

    def test_user_login_valid(
        self,
        api_manager: ApiManager,
        create_user_request: CreateUserRequest,
    ):
        """Позитивный тест: успешная авторизация созданного пользователя."""
        # Act
        response = api_manager.user_steps.login_user(create_user_request)

        # Assert
        assert response.user.username == create_user_request.username, \
            f"Не совпал логин при авторизации пользователем, пришел {response.user.username} вместо {create_user_request.username}"
        assert response.user.role == 'ROLE_USER', f"Роль не юзер, a {response.user.role}"
