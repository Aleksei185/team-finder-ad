"""Тесты для представлений проектов."""
import pytest
from projects.models import Project


@pytest.mark.django_db
class TestProjectViews:
    """Тесты страниц и действий с проектами."""

    def test_create_project_requires_login(self, client):
        """Создание проекта требует авторизации."""
        response = client.get('/projects/create-project/')
        assert response.status_code == 302
        assert '/users/login/' in response.url

    def test_create_project_success(self, client, user):
        """Успешное создание проекта."""
        client.login(email=user.email, password='testpass')
        data = {
            'name': 'New Project',
            'description': 'Desc',
            'status': 'open',
            'github_url': 'https://github.com/test/repo'
        }
        response = client.post('/projects/create-project/', data)
        assert response.status_code == 302
        project = Project.objects.get(name='New Project')
        assert project.owner == user
        assert user in project.participants.all()

    def test_project_detail_page(self, client, project):
        """Страница деталей проекта доступна."""
        response = client.get(f'/projects/{project.id}/')
        assert response.status_code == 200
        assert project.name in response.content.decode()

    def test_toggle_participate(self, client, project, second_user):
        """Авторизованный пользователь может присоединиться и отказаться."""
        client.login(email=second_user.email, password='testpass')
        url = f'/projects/{project.id}/toggle-participate/'
        # Присоединение
        response = client.post(url)
        assert response.status_code == 200
        assert second_user in project.participants.all()
        # Отказ
        response2 = client.post(url)
        assert response2.status_code == 200
        assert second_user not in project.participants.all()

    def test_complete_project(self, client, project, user):
        """Владелец может завершить проект."""
        client.login(email=user.email, password='testpass')
        url = f'/projects/{project.id}/complete/'
        response = client.post(url)
        assert response.status_code == 200
        project.refresh_from_db()
        assert project.status == 'closed'
