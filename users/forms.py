# 1. Стандартные библиотеки
import re

# 2. Сторонние библиотеки
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import URLValidator

# 3. Модули этого проекта
from common.constants import PHONE_REGEX
from common.mixins import GitHubURLMixin
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )


class UserEditForm(GitHubURLMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Приводим 8... к +7...
            if phone.startswith('8') and len(phone) == 11:
                phone = '+7' + phone[1:]

            # Проверяем формат +7XXXXXXXXXX
            if not re.match(PHONE_REGEX, phone):
                raise ValidationError(
                    'Номер телефона должен быть в формате '
                    '+7XXXXXXXXXX (10 цифр после +7)'
                )

            # Проверка уникальности
            if self.instance and self.instance.pk:
                if User.objects.exclude(
                    pk=self.instance.pk
                ).filter(phone=phone).exists():
                    raise ValidationError(
                        'Этот номер телефона уже используется'
                    )
            else:
                if User.objects.filter(phone=phone).exists():
                    raise ValidationError(
                        'Этот номер телефона уже используется'
                    )

        return phone
