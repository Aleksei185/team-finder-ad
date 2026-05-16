from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Project
from .forms import ProjectForm


def project_list(request):
    projects_qs = Project.objects.all()
    paginator = Paginator(projects_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    query_prefix = ''
    if request.GET.urlencode():
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        if query_params:
            query_prefix = query_params.urlencode() + '&'
    return render(
        request,
        'projects/project_list.html',
        {'page_obj': page_obj, 'query_prefix': query_prefix}
    )


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(
        request,
        'projects/project-details.html',
        {'project': project}
    )


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # автор становится участником
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm()
    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return redirect('/projects/list/')
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': True}
    )


@require_http_methods(['POST'])
@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if project.status == 'open':
        project.status = 'closed'
        project.save()
        return JsonResponse(
            {'status': 'ok', 'project_status': 'closed'}
        )
    return JsonResponse({'error': 'Project already closed'}, status=400)


@require_http_methods(['POST'])
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner == request.user:
        return JsonResponse(
            {'error': 'Owner cannot participate'},
            status=400
        )
    user = request.user
    if user in project.participants.all():
        project.participants.remove(user)
        is_participating = False
    else:
        project.participants.add(user)
        is_participating = True
    return JsonResponse(
        {'status': 'ok', 'is_participating': is_participating}
    )
