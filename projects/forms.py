from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import Project
from common.mixins import GitHubURLMixin


class ProjectForm(GitHubURLMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
        widgets = {
            'status': forms.Select(choices=Project.STATUS_CHOICES),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
