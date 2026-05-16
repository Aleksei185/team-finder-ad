"""Тесты API для работы с навыками (автодополнение, добавление, удаление)."""
import json
import pytest
from users.models import Skill


@pytest.mark.django_db
class TestSkillsAPI:
    """Тесты API навыков."""

    def test_skills_autocomplete(self, client, skill_python):
        """GET /users/skills/?q=Py возвращает список навыков."""
        response = client.get('/users/skills/?q=Py')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Python'

    def test_add_skill_by_id(self, client, user, skill_python):
        """Добавление существующего навыка по ID."""
        client.login(email=user.email, password='testpass')
        url = f'/users/{user.id}/skills/add/'
        response = client.post(
            url,
            data=json.dumps({'skill_id': skill_python.id}),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert user.skills.filter(id=skill_python.id).exists()
        assert response.json()['added'] is True

    def test_add_skill_by_name_new(self, client, user):
        """Создание и добавление нового навыка по имени."""
        client.login(email=user.email, password='testpass')
        url = f'/users/{user.id}/skills/add/'
        response = client.post(
            url,
            data=json.dumps({'name': 'Django'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert Skill.objects.filter(name='Django').exists()
        assert user.skills.filter(name='Django').exists()
        assert response.json()['created'] is True

    def test_add_skill_duplicate(self, client, user, skill_python):
        """Попытка добавить уже существующий у пользователя навык."""
        user.skills.add(skill_python)
        client.login(email=user.email, password='testpass')
        url = f'/users/{user.id}/skills/add/'
        response = client.post(
            url,
            data=json.dumps({'skill_id': skill_python.id}),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.json()['added'] is False

    def test_remove_skill(self, client, user, skill_python):
        """Удаление навыка у пользователя."""
        user.skills.add(skill_python)
        client.login(email=user.email, password='testpass')
        url = f'/users/{user.id}/skills/{skill_python.id}/remove/'
        response = client.post(url)
        assert response.status_code == 200
        assert not user.skills.filter(id=skill_python.id).exists()
