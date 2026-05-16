"""Тесты для представлений пользователей (регистрация, логин, профиль)."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestUserViews:
    """Тесты страниц пользователей."""

    def test_register_page(self, client):
        """Страница регистрации доступна."""
        response = client.get('/users/register/')
        assert response.status_code == 200
        assert 'users/register.html' in [t.name for t in response.templates]

    def test_register_success(self, client):
        """Успешная регистрация перенаправляет на список проектов."""
        data = {
            'email': 'new@test.com',
            'name': 'New',
            'surname': 'User',
            'password': 'pass12345'
        }
        response = client.post('/users/register/', data)
        assert response.status_code == 302
        assert response.url == '/projects/list/'

    def test_login_page(self, client):
        """Страница входа доступна."""
        response = client.get('/users/login/')
        assert response.status_code == 200

    def test_login_success(self, client, user):
        """Успешный вход перенаправляет на список проектов."""
        response = client.post(
            '/users/login/',
            {'email': user.email, 'password': 'testpass'}
        )
        assert response.status_code == 302
        assert response.url == '/projects/list/'

    def test_login_invalid(self, client):
        """Неверные данные логина показывают ошибку."""
        response = client.post(
            '/users/login/',
            {'email': 'wrong@test.com', 'password': 'wrong'}
        )
        assert response.status_code == 200
        assert 'Неверный имейл или пароль' in response.content.decode()

    def test_user_detail_page(self, client, user):
        """Страница пользователя отображает его данные."""
        response = client.get(f'/users/{user.id}/')
        assert response.status_code == 200
        assert user.name in response.content.decode()

    def test_edit_profile_requires_login(self, client):
        """Редактирование профиля требует авторизации."""
        response = client.get('/users/edit-profile/')
        assert response.status_code == 302
        assert '/users/login/' in response.url
