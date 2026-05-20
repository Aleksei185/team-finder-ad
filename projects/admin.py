from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Настройка отображения проектов в админке."""
    list_display = ('id', 'name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'owner')
    search_fields = ('name', 'description', 'owner__email', 'owner__name')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner', 'github_url', 'status')
        }),
        ('Участники', {'fields': ('participants',)}),
        ('Даты', {'fields': ('created_at',)}),
    )
