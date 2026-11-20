from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreateForm, UserEditForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserEditForm
    add_form = UserCreateForm
    ordering = ('email',)
    list_display = ('email', 'name', 'surname', 'is_active', 'is_staff')
    search_fields = ('email', 'name', 'surname')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Профиль', {'fields': (
            'name', 'surname', 'avatar', 'phone', 'github_url', 'about',
        )}),
        ('Права', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions',
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'password1', 'password2',
            ),
        }),
    )
