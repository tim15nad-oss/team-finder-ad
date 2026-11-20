from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .constants import (
    PHONE_INPUT_MAX_LENGTH,
    PHONE_INTERNATIONAL_PREFIX,
    PHONE_LOCAL_PREFIX,
    PHONE_PATTERN,
    PHONE_SEPARATORS,
)
from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль', widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'email')

    def clean_email(self) -> str:
        return self.cleaned_data['email'].lower()

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self) -> dict:
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email.lower(), password=password)
            if user is None:
                raise forms.ValidationError('Неверный имейл или пароль')
            self.user = user
        return cleaned_data


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label='Аватар', required=False)
    phone = forms.CharField(
        label='Телефон', required=False, max_length=PHONE_INPUT_MAX_LENGTH
    )

    class Meta:
        model = User
        fields = (
            'name', 'surname', 'avatar', 'about', 'phone', 'github_url'
        )

    def clean_phone(self):
        raw = self.cleaned_data.get('phone') or ''
        phone = PHONE_SEPARATORS.sub('', raw)
        if not phone:
            return None
        if not PHONE_PATTERN.fullmatch(phone):
            raise forms.ValidationError(
                'Телефон: 8XXXXXXXXXX или +7XXXXXXXXXX.'
            )
        if phone.startswith(PHONE_LOCAL_PREFIX):
            local_part = phone[len(PHONE_LOCAL_PREFIX):]
            phone = PHONE_INTERNATIONAL_PREFIX + local_part
        taken = User.objects.filter(phone=phone)
        if taken.exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот телефон уже занят.')
        return phone


class UserCreateForm(BaseUserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'name', 'surname')


class UserEditForm(UserChangeForm):

    class Meta:
        model = User
        fields = '__all__'
