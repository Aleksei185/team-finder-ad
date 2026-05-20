from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Настройка отображения навыков в админке."""
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройка отображения пользователей в админке."""
    list_display = (
        'id', 'email', 'name', 'surname', 'phone', 'is_active',
        'is_staff', 'created_at'
    )
    list_filter = ('is_active', 'is_staff', 'skills')
    search_fields = ('email', 'name', 'surname', 'phone')

    # ordering переопределено, потому что родительский класс BaseUserAdmin
    # использует сортировку по полю username, которого нет в кастомной модели.
    # Явное указание сортировки по -created_at устраняет ошибку admin.E033.
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {
            'fields': (
                'name', 'surname', 'avatar', 'phone', 'github_url', 'about'
            )
        }),
        ('Навыки', {'fields': ('skills',)}),
        ('Права доступа', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        ('Важные даты', {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'password1', 'password2', 'phone'
            ),
        }),
    )

    # readonly_fields оставляем — это запрещает редактирование даты создания
    readonly_fields = ('created_at',)
