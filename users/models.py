from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.validators import RegexValidator
from django.db import models
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import random
import hashlib


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, name, surname, password=None, **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField(
        max_length=124,
        unique=True,
        verbose_name='Название навыка'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=124, verbose_name='Имя')
    surname = models.CharField(max_length=124, verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r'^\+7\d{10}$',
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
        max_length=256,
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
        size = 200
        color = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        image = Image.new('RGB', (size, size), color)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except Exception:  # noqa: BLE001
            font = ImageFont.load_default()
        letter = self.name[0].upper() if self.name else '?'
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (
            (size - text_width) // 2,
            (size - text_height) // 2
        )
        draw.text(position, letter, fill='white', font=font)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        email_hash = hashlib.md5(self.email.encode()).hexdigest()
        filename = f'avatar_{email_hash}.png'
        return ContentFile(buffer.getvalue(), name=filename)
