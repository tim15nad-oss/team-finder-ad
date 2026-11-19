import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project, Skill

PAGE_SIZE = 12
SUGGEST_LIMIT = 10
SKILL_NAME_MAX = 124


def project_list(request):
    projects = (
        Project.objects.select_related('owner')
        .prefetch_related('participants')
        .order_by('-created_at')
    )
    active_skill = request.GET.get('skill', '').strip()
    if active_skill:
        projects = projects.filter(skills__name=active_skill)
    page_obj = Paginator(projects, PAGE_SIZE).get_page(
        request.GET.get('page')
    )
    context = {
        'projects': page_obj,
        'page_obj': page_obj,
        'all_skills': Skill.objects.values_list('name', flat=True),
        'active_skill': active_skill,
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
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:project_detail', project_id=project.pk)
    context = {'form': form, 'is_edit': False}
    return render(request, 'projects/create-project.html', context)


@login_required
def edit_project(request, project_id: int):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        raise PermissionDenied
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('projects:project_detail', project_id=project.pk)
    context = {'form': form, 'is_edit': True}
    return render(request, 'projects/create-project.html', context)


def _error(message: str, status: int) -> JsonResponse:
    return JsonResponse({'status': 'error', 'message': message}, status=status)


def _read_body(request) -> dict:
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body or '{}')
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}
    return request.POST


@require_POST
def complete_project(request, project_id: int):
    if not request.user.is_authenticated:
        return _error('Нужен вход.', 401)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return _error('Нет прав.', 403)
    if project.status != 'open':
        return _error('Проект уже закрыт.', 400)
    project.status = 'closed'
    project.save(update_fields=['status'])
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


@require_POST
def toggle_participate(request, project_id: int):
    if not request.user.is_authenticated:
        return _error('Нужен вход.', 401)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner == request.user:
        return _error('Автор не может выйти из проекта.', 400)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({'status': 'ok', 'participant': participant})


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
        return _error('Нужен вход.', 401)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return _error('Нет прав.', 403)
    data = _read_body(request)
    skill_id = data.get('skill_id')
    name = str(data.get('name') or '').strip()
    created = False
    if skill_id not in (None, ''):
        try:
            skill = Skill.objects.get(pk=int(skill_id))
        except (ValueError, TypeError, Skill.DoesNotExist):
            return _error('Навык не найден.', 404)
    elif name and len(name) <= SKILL_NAME_MAX:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return _error('Нужен skill_id или корректный name.', 400)
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
        return _error('Нужен вход.', 401)
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return _error('Нет прав.', 403)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return _error('У проекта нет этого навыка.', 404)
    project.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
