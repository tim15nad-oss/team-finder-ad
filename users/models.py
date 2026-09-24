from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from .avatars import make_avatar_file
from .validators import validate_github_url


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError('Email обязателен')
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Имя', max_length=124)
    surname = models.CharField('Фамилия', max_length=124)
    avatar = models.ImageField('Аватар', upload_to='avatars/')
    # Телефон нужен по заданию, но в форме регистрации его нет, поэтому поле может
    # быть пустым (NULL). unique допускает много NULL. Отметьте это в README.
    phone = models.CharField('Телефон', max_length=12, unique=True, null=True, blank=True)
    github_url = models.URLField('GitHub', blank=True, validators=[validate_github_url])
    about = models.TextField('О себе', max_length=256, blank=True)
    is_active = models.BooleanField('Активный', default=True)
    is_staff = models.BooleanField('Администратор', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.avatar:     # первая аватарка генерируется перед сохранением в БД
            self.avatar.save(f'{uuid4().hex}.png', make_avatar_file(self.name), save=False)
        super().save(*args, **kwargs)