from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from .avatars import make_avatar
from .validators import validate_github_url


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Имя', max_length=124)
    surname = models.CharField('Фамилия', max_length=124)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    phone = models.CharField(
        'Телефон', max_length=12, unique=True, null=True, blank=True
    )
    github_url = models.URLField(
        'GitHub', blank=True, validators=[validate_github_url]
    )
    about = models.TextField('О себе', max_length=256, blank=True)
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

    def save(self, *args, **kwargs) -> None:
        if not self.avatar:
            content = make_avatar(self.name[:1].upper() or '?')
            self.avatar.save(content.name, content, save=False)
        super().save(*args, **kwargs)
