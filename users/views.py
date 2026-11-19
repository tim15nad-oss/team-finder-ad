from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User

PAGE_SIZE = 12


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('users:login')
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.user)
        return redirect('projects:project_list')
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('projects:project_list')


def user_list(request):
    users = User.objects.order_by('-id')
    page_obj = Paginator(users, PAGE_SIZE).get_page(request.GET.get('page'))
    context = {'participants': page_obj, 'page_obj': page_obj}
    return render(request, 'users/participants.html', context)


def user_detail(request, user_id: int):
    profile = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile})


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('users:user_detail', user_id=request.user.pk)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('users:user_detail', user_id=user.pk)
    return render(request, 'users/change_password.html', {'form': form})
