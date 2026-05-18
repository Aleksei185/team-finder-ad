from django.conf import settings
from django.db import models

from common.constants import (
    MAX_LENGTH_PROJECT_NAME,
    MAX_LENGTH_PROJECT_STATUS,
    PROJECT_STATUS_OPEN,
    PROJECT_STATUS_CLOSED,
)


class Project(models.Model):
    STATUS_CHOICES = (
        (PROJECT_STATUS_OPEN, 'Открыт'),
        (PROJECT_STATUS_CLOSED, 'Закрыт'),
    )

    name = models.CharField(
        max_length=MAX_LENGTH_PROJECT_NAME,
        verbose_name='Название проекта'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='GitHub'
    )
    status = models.CharField(
        max_length=MAX_LENGTH_PROJECT_STATUS,
        choices=STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name='Статус'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
