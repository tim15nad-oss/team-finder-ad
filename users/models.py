from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse

from .avatars import make_avatar
from .constants import (
    ABOUT_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
)
from .managers import UserManager
from .validators import validate_github_url


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Имя', max_length=NAME_MAX_LENGTH)
    surname = models.CharField('Фамилия', max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    phone = models.CharField(
        'Телефон',
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        null=True,
        blank=True,
    )
    github_url = models.URLField(
        'GitHub', blank=True, validators=[validate_github_url]
    )
    about = models.TextField('О себе', max_length=ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField('Сотрудник', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email

    def get_absolute_url(self) -> str:
        return reverse('users:user_detail', kwargs={'user_id': self.pk})

    def save(self, *args, **kwargs) -> None:
        if not self.avatar:
            content = make_avatar(self.name[:1].upper() or '?')
            self.avatar.save(content.name, content, save=False)
        super().save(*args, **kwargs)
