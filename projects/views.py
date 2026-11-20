from http import HTTPStatus
from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from team_finder.service import paginate

from .constants import (
    SKILL_NAME_MAX_LENGTH,
    STATUS_CLOSED,
    STATUS_OPEN,
    SUGGEST_LIMIT,
)
from .forms import ProjectForm
from .models import Project, Skill
from .service import json_error, read_body


def project_list(request):
    projects = (
        Project.objects.select_related('owner')
        .prefetch_related('participants')
        .order_by('-created_at')
    )
    active_skill = request.GET.get('skill', '').strip()
    if active_skill:
        projects = projects.filter(skills__name=active_skill)
    page_obj = paginate(request, projects)

    query_prefix = f'skill={quote(active_skill)}&' if active_skill else ''
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'all_skills': Skill.objects.values_list('name', flat=True),
        'active_skill': active_skill,
        'query_prefix': query_prefix,
    }
    return render(request, 'projects/project_list.html', context)


@ensure_csrf_cookie
def project_detail(request, project_id: int):
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related(
            'participants', 'skills'
        ),
        pk=project_id,
    )
    return render(
        request, 'projects/project-details.html', {'project': project}
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(project)
    context = {'form': form, 'is_edit': False}
    return render(request, 'projects/create-project.html', context)


@login_required
def edit_project(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        raise PermissionDenied
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect(project)
    context = {'form': form, 'is_edit': True}
    return render(request, 'projects/create-project.html', context)


@require_POST
def complete_project(request, project_id: int):
    if not request.user.is_authenticated:
        return json_error('Нужен вход.', HTTPStatus.UNAUTHORIZED)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return json_error('Нет прав.', HTTPStatus.FORBIDDEN)
    if project.status != STATUS_OPEN:
        return json_error('Проект уже закрыт.', HTTPStatus.BAD_REQUEST)
    project.status = STATUS_CLOSED
    project.save(update_fields=['status'])
    return JsonResponse({'status': 'ok', 'project_status': project.status})


@require_POST
def toggle_participate(request, project_id: int):
    if not request.user.is_authenticated:
        return json_error('Нужен вход.', HTTPStatus.UNAUTHORIZED)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner == request.user:
        return json_error(
            'Автор не может выйти из проекта.', HTTPStatus.BAD_REQUEST
        )
    is_participant = project.participants.filter(pk=request.user.pk).exists()
    change_participation = (
        project.participants.remove if is_participant
        else project.participants.add
    )
    change_participation(request.user)
    return JsonResponse({'status': 'ok', 'participant': not is_participant})


@require_GET
def skill_search(request):
    query = request.GET.get('q', '').strip()
    skills = (
        Skill.objects.filter(name__istartswith=query)
        .order_by('name')
        .values('id', 'name')[:SUGGEST_LIMIT]
    )
    return JsonResponse(list(skills), safe=False)


@require_POST
def add_skill(request, project_id: int):
    if not request.user.is_authenticated:
        return json_error('Нужен вход.', HTTPStatus.UNAUTHORIZED)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return json_error('Нет прав.', HTTPStatus.FORBIDDEN)
    data = read_body(request)
    skill_id = data.get('skill_id')
    name = str(data.get('name') or '').strip()
    created = False
    if skill_id not in (None, ''):
        try:
            skill = Skill.objects.get(pk=int(skill_id))
        except (ValueError, TypeError, Skill.DoesNotExist):
            return json_error('Навык не найден.', HTTPStatus.NOT_FOUND)
    elif name and len(name) <= SKILL_NAME_MAX_LENGTH:
        skill = Skill.objects.filter(name__iexact=name).first()
        created = skill is None
        if created:
            skill = Skill.objects.create(name=name)
    else:
        return json_error(
            'Нужен skill_id или корректный name.', HTTPStatus.BAD_REQUEST
        )
    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)
    return JsonResponse({
        'status': 'ok',
        'skill_id': skill.pk,
        'created': created,
        'added': added,
        'id': skill.pk,
        'name': skill.name,
    })


@require_POST
def remove_skill(request, project_id: int, skill_id: int):
    if not request.user.is_authenticated:
        return json_error('Нужен вход.', HTTPStatus.UNAUTHORIZED)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return json_error('Нет прав.', HTTPStatus.FORBIDDEN)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return json_error(
            'У проекта нет этого навыка.', HTTPStatus.NOT_FOUND
        )
    project.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
