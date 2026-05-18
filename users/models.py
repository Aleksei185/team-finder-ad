import hashlib
import random
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from common.constants import (
    AVATAR_ANCHOR_OFFSET,
    AVATAR_BG_COLOR_MAX,
    AVATAR_BG_COLOR_MIN,
    AVATAR_FONT_PATH,
    AVATAR_FONT_SIZE,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    MAX_LENGTH_ABOUT,
    MAX_LENGTH_NAME,
    MAX_LENGTH_PHONE,
    MAX_LENGTH_SKILL_NAME,
    MAX_LENGTH_SURNAME,
    PHONE_REGEX,
)
from users.managers import UserManager


class Skill(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_SKILL_NAME,
        unique=True,
        verbose_name='Название навыка'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=MAX_LENGTH_NAME, verbose_name='Имя')
    surname = models.CharField(
        max_length=MAX_LENGTH_SURNAME,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=MAX_LENGTH_PHONE,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                PHONE_REGEX,
                'Номер телефона должен быть в формате +7XXXXXXXXXX'
            )
        ],
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='GitHub'
    )
    about = models.TextField(
        max_length=MAX_LENGTH_ABOUT,
        blank=True,
        verbose_name='О себе'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField(
        'Skill',
        related_name='users',
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        color = tuple(
            random.randint(AVATAR_BG_COLOR_MIN, AVATAR_BG_COLOR_MAX)
            for _ in range(3)
        )
        image = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(AVATAR_FONT_PATH, AVATAR_FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()

        letter = self.name[0].upper() if self.name else '?'
        bbox = draw.textbbox(
            (AVATAR_ANCHOR_OFFSET, AVATAR_ANCHOR_OFFSET),
            letter,
            font=font
        )
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (
            (AVATAR_SIZE - text_width) // 2,
            (AVATAR_SIZE - text_height) // 2
        )
        draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        email_hash = hashlib.md5(self.email.encode()).hexdigest()
        filename = f'avatar_{email_hash}.png'
        return ContentFile(buffer.getvalue(), name=filename)
