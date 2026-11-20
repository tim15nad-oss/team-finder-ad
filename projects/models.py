from django.conf import settings
from django.db import models
from django.urls import reverse

from users.validators import validate_github_url

from .constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    STATUS_CHOICES,
    STATUS_OPEN,
)


class Skill(models.Model):
    name = models.CharField(
        'Название', max_length=SKILL_NAME_MAX_LENGTH, unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    name = models.CharField('Название', max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField('Описание', blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(
        'Дата создания', auto_now_add=True, db_index=True
    )
    github_url = models.URLField(
        'GitHub', blank=True, validators=[validate_github_url]
    )
    status = models.CharField(
        'Статус',
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill, related_name='projects', blank=True
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            'projects:project_detail', kwargs={'project_id': self.pk}
        )
