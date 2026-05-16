"""Тесты фильтрации списка пользователей по навыкам."""
import pytest


@pytest.mark.django_db
class TestFilters:
    """Тесты фильтрации."""

    def test_user_list_filter_by_skill(
        self, client, user, second_user, skill_python, skill_cpp
    ):
        """Фильтр по навыку оставляет только пользователей с этим навыком."""
        second_user.skills.add(skill_python)   # у второго есть Python
        user.skills.add(skill_cpp)             # у первого есть C++
        response = client.get('/users/list/?skill=Python')
        assert response.status_code == 200
        content = response.content.decode()
        assert second_user.name in content
        assert user.name not in content

    def test_user_list_filter_case_insensitive(
            self, client, user, skill_python
    ):
        """Фильтр не чувствителен к регистру."""
        user.skills.add(skill_python)
        response = client.get('/users/list/?skill=python')  # нижний регистр
        assert response.status_code == 200
        assert user.name in response.content.decode()

    def test_user_list_filter_nonexistent_skill_returns_empty(self, client):
        """Фильтр по несуществующему навыку возвращает пустой список."""
        response = client.get('/users/list/?skill=NonExistent')
        assert response.status_code == 200
        # Проверяем наличие сообщения о пустом списке (зависит от шаблона)
        assert 'Пока нет участников' in response.content.decode()
