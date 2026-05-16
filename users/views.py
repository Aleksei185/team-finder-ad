from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, Skill
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm
import json


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/projects/list/')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/projects/list/')
            else:
                form.add_error(None, 'Неверный имейл или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('/projects/list/')


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/user_details.html', {'user': user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f'/users/{request.user.id}/')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def user_list(request):
    users_qs = User.objects.all()
    all_skills = Skill.objects.all()
    active_skill = request.GET.get('skill')
    if active_skill:
        # регистронезависимый поиск
        skill_obj = Skill.objects.filter(
            name__iexact=active_skill
        ).first()
        if skill_obj:
            users_qs = users_qs.filter(skills=skill_obj)
            active_skill = skill_obj.name
    paginator = Paginator(users_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_prefix = query_params.urlencode()
    if query_prefix:
        query_prefix += '&'
    return render(
        request,
        'users/participants.html',
        {
            'page_obj': page_obj,
            'all_skills': all_skills,
            'active_skill': active_skill,
            'query_prefix': query_prefix,
        }
    )


# API для навыков
@require_http_methods(['GET'])
def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q)[:10]
    data = [{'id': s.id, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)


@require_http_methods(['POST'])
@login_required
def add_skill(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    user = get_object_or_404(User, id=user_id)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    created = False
    added = False
    skill = None
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
            status=400
        )
    if skill:
        if skill not in user.skills.all():
            user.skills.add(skill)
            added = True
        # Возвращаем также name, чтобы фронтенд мог отобразить название
        return JsonResponse({
            'skill_id': skill.id,
            'created': created,
            'added': added,
            'name': skill.name
        })
    return JsonResponse({'error': 'Skill not found'}, status=404)


@require_http_methods(['POST'])
@login_required
def remove_skill(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    user = get_object_or_404(User, id=user_id)
    skill = get_object_or_404(Skill, id=skill_id)
    if skill in user.skills.all():
        user.skills.remove(skill)
        return JsonResponse({'removed': True})
    else:
        return JsonResponse(
            {'error': 'Skill not in user'},
            status=400
        )
