from django.conf import settings
from django.db import models

from users.validators import validate_github_url


class Skill(models.Model):
    name = models.CharField('Название', max_length=124, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    name = models.CharField('Название', max_length=200)
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
        'Статус', max_length=6, choices=STATUS_CHOICES, default='open'
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
