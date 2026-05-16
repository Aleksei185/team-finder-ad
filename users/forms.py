from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from .models import User
import re


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


class UserEditForm(forms.ModelForm):
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
            pattern = r'^\+7\d{10}$'
            if not re.match(pattern, phone):
                raise ValidationError(
                    'Номер телефона должен быть в формате '
                    '+7XXXXXXXXXX (10 цифр после +7)'
                )
            # Уникальность
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

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if not url.startswith('http'):
                url = 'https://' + url
            try:
                URLValidator()(url)
            except ValidationError:
                raise ValidationError('Введите корректный URL')
            if 'github.com' not in url:
                raise ValidationError(
                    'Ссылка должна вести на GitHub'
                )
        return url
