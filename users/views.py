from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.service import paginate

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('users:login')
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.user)
        return redirect('projects:project_list')
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('projects:project_list')


def user_list(request):
    page_obj = paginate(request, User.objects.order_by('-id'))
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
    if form.is_valid():
        form.save()
        return redirect(request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect(user)
    return render(request, 'users/change_password.html', {'form': form})
