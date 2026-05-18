from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.decorators.http import require_http_methods

from common.constants import PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED
from common.services import paginate_queryset
from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects_qs = Project.objects.annotate(
        participants_count=Count('participants')
    ).select_related('owner')

    page_obj, query_prefix = paginate_queryset(request, projects_qs)

    return render(
        request,
        'projects/project_list.html',
        {'page_obj': page_obj, 'query_prefix': query_prefix}
    )


def project_detail(request, project_id):
    queryset = Project.objects.select_related('owner').prefetch_related(
        'participants'
    )
    project = get_object_or_404(queryset, id=project_id)
    return render(
        request,
        'projects/project-details.html',
        {'project': project}
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(reverse('projects:project_detail', args=[project.id]))
    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return redirect(reverse('projects:project_list'))

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect(reverse('projects:project_detail', args=[project.id]))

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
        return JsonResponse(
            {'error': 'Forbidden'},
            status=HTTPStatus.FORBIDDEN
        )
    if project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse(
            {'status': 'ok', 'project_status': PROJECT_STATUS_CLOSED},
            status=HTTPStatus.OK
        )
    return JsonResponse(
        {'error': 'Project already closed'},
        status=HTTPStatus.BAD_REQUEST
    )


@require_http_methods(['POST'])
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner == request.user:
        return JsonResponse(
            {'error': 'Owner cannot participate'},
            status=HTTPStatus.BAD_REQUEST
        )

    user = request.user
    is_participating = project.participants.filter(id=user.id).exists()

    if is_participating:
        project.participants.remove(user)
    else:
        project.participants.add(user)

    return JsonResponse(
        {'status': 'ok', 'is_participating': not is_participating},
        status=HTTPStatus.OK
    )
