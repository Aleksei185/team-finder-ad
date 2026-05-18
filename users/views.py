from http import HTTPStatus
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from common.constants import ITEMS_PER_PAGE, SKILLS_AUTOCOMPLETE_LIMIT
from common.services import paginate_queryset
from .forms import UserEditForm, UserLoginForm, UserRegistrationForm
from .models import Skill, User


def register(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(reverse('projects:project_list'))
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('projects:project_list'))
        form.add_error(None, 'Неверный имейл или пароль')
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('projects:project_list'))


def user_detail(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    return render(request, 'users/user_details.html', {'user': user_instance})


@login_required
def edit_profile(request):
    form = UserEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect(reverse('users:user_detail', args=[request.user.id]))
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect(reverse('users:user_detail', args=[request.user.id]))
    return render(request, 'users/change_password.html', {'form': form})


def user_list(request):
    users_queryset = User.objects.all()
    all_skills = Skill.objects.all()
    active_skill = request.GET.get('skill')
    if active_skill:
        skill_object = Skill.objects.filter(
            name__iexact=active_skill
        ).first()
        if skill_object:
            users_queryset = users_queryset.filter(skills=skill_object)
            active_skill = skill_object.name
        else:
            users_queryset = User.objects.none()

    page_object, query_prefix = paginate_queryset(request, users_queryset)

    return render(
        request,
        'users/participants.html',
        {
            'page_obj': page_object,
            'all_skills': all_skills,
            'active_skill': active_skill,
            'query_prefix': query_prefix,
        }
    )


# API для навыков
@require_http_methods(['GET'])
def skills_autocomplete(request):
    search_query = request.GET.get('q', '')
    skills = Skill.objects.filter(
        name__istartswith=search_query
    )[:SKILLS_AUTOCOMPLETE_LIMIT]
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@require_http_methods(['POST'])
@login_required
def add_skill(request, user_id):
    if request.user.id != user_id:
        return JsonResponse(
            {'error': 'Forbidden'},
            status=HTTPStatus.FORBIDDEN
        )
    user_instance = get_object_or_404(User, id=user_id)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse(
            {'error': 'Invalid JSON'},
            status=HTTPStatus.BAD_REQUEST
        )
    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    created = False
    added = False
    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(
            name__iexact=skill_name,
            defaults={'name': skill_name}
        )
    else:
        return JsonResponse(
            {'error': 'skill_id or name required'},
            status=HTTPStatus.BAD_REQUEST
        )
    if skill:
        if not user_instance.skills.filter(id=skill.id).exists():
            user_instance.skills.add(skill)
            added = True
        return JsonResponse({
            'skill_id': skill.id,
            'created': created,
            'added': added,
            'name': skill.name
        })
    return JsonResponse(
        {'error': 'Skill not found'},
        status=HTTPStatus.NOT_FOUND
    )


@require_http_methods(['POST'])
@login_required
def remove_skill(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse(
            {'error': 'Forbidden'},
            status=HTTPStatus.FORBIDDEN
        )
    user_instance = get_object_or_404(User, id=user_id)
    skill = get_object_or_404(Skill, id=skill_id)
    if user_instance.skills.filter(id=skill.id).exists():
        user_instance.skills.remove(skill)
        return JsonResponse({'removed': True})
    return JsonResponse(
        {'error': 'Skill not in user'},
        status=HTTPStatus.BAD_REQUEST
    )
