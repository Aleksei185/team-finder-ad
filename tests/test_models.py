"""Тесты для моделей users и projects."""
import pytest
from django.contrib.auth import get_user_model
from users.models import Skill
from projects.models import Project

User = get_user_model()


def test_create_user(db):
    """Создание обычного пользователя."""
    user = User.objects.create_user(
        email='test@test.com',
        name='John',
        surname='Doe',
        password='pass',
        phone='+71234567890'
    )
    assert user.email == 'test@test.com'
    assert user.name == 'John'


def test_user_avatar_generated_on_create(db):
    """Аватар генерируется при создании пользователя."""
    user = User.objects.create_user(
        email='avatar@test.com',
        name='Anna',
        surname='Smith',
        password='pass',
        phone='+71234567891'
    )
    assert user.avatar.name.startswith('avatars/avatar_')


def test_create_skill(db):
    """Создание навыка."""
    skill = Skill.objects.create(name='Python')
    assert str(skill) == 'Python'


def test_create_project(db, user):
    """Создание проекта."""
    project = Project.objects.create(
        name='My Project',
        description='Desc',
        owner=user,
        status='open'
    )
    assert str(project) == 'My Project'
    assert project.owner == user
    assert project.status == 'open'
