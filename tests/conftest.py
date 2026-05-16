"""Фикстуры для всех тестов."""
import pytest
from django.contrib.auth import get_user_model
from users.models import Skill
from projects.models import Project

User = get_user_model()


@pytest.fixture
def client():
    """Клиент для HTTP-запросов."""
    from django.test import Client
    return Client()


@pytest.fixture
def user(db):
    """Обычный пользователь."""
    return User.objects.create_user(
        email='user@test.com',
        name='Test',
        surname='User',
        password='testpass',
        phone='+71234567890'
    )


@pytest.fixture
def second_user(db):
    """Второй пользователь для проверки участия в проектах."""
    return User.objects.create_user(
        email='user2@test.com',
        name='Second',
        surname='User',
        password='testpass',
        phone='+79876543210'
    )


@pytest.fixture
def admin_user(db):
    """Суперпользователь для тестов админки."""
    return User.objects.create_superuser(
        email='admin@test.com',
        name='Admin',
        surname='User',
        password='adminpass'
    )


@pytest.fixture
def skill_python(db):
    """Навык Python."""
    return Skill.objects.create(name='Python')


@pytest.fixture
def skill_cpp(db):
    """Навык C++."""
    return Skill.objects.create(name='C++')


@pytest.fixture
def project(db, user):
    """Проект, созданный обычным пользователем."""
    return Project.objects.create(
        name='Test Project',
        description='Description',
        owner=user,
        status='open'
    )
