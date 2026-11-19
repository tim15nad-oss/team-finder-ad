import re

from django import forms
from django.contrib.auth import authenticate

from .models import User

PHONE_RE = re.compile(r'(8|\+7)\d{10}')


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

    class Meta:
        model = User
        fields = (
            'name', 'surname', 'avatar', 'about', 'phone', 'github_url'
        )

    def clean_phone(self):
        raw = self.cleaned_data.get('phone') or ''
        phone = re.sub(r'[\s()\-]', '', raw)
        if not phone:
            return None
        if not PHONE_RE.fullmatch(phone):
            raise forms.ValidationError(
                'Телефон: 8XXXXXXXXXX или +7XXXXXXXXXX.'
            )
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        taken = User.objects.filter(phone=phone)
        if taken.exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот телефон уже занят.')
        return phone
