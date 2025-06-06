from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.conf import settings
import re

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control py-4',
            'placeholder': 'Введите имя пользователя',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-4',
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password'
        })
    )

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control py-4',
            'placeholder': 'Введите email',
            'autocomplete': 'email'
        }),
        help_text="На этот email будут приходить уведомления"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control py-4',
                'placeholder': 'Введите имя пользователя',
                'autocomplete': 'username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control py-4',
                'placeholder': 'Введите пароль',
                'autocomplete': 'new-password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control py-4',
                'placeholder': 'Подтвердите пароль',
                'autocomplete': 'new-password'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'image')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'placeholder': 'Введите имя',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'placeholder': 'Введите фамилию',
                'autocomplete': 'family-name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control py-2',
                'readonly': True,
                'autocomplete': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'placeholder': '+7 (___) ___ __ __',
                'data-mask': '+7 (999) 999-99-99',
                'autocomplete': 'tel'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control py-2',
                'type': 'date',
                'autocomplete': 'bday'
            }, format='%Y-%m-%d'),
            'image': forms.FileInput(attrs={
                'class': 'form-control-file d-none',
                'accept': 'image/jpeg, image/png, image/webp',
                'id': 'avatar-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.birth_date:
            self.initial['birth_date'] = self.instance.birth_date.strftime('%Y-%m-%d')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            cleaned = re.sub(r'[^\d+]', '', phone)
            if not cleaned.startswith('+7') or len(cleaned) != 12:
                raise ValidationError("Номер должен быть в формате +7XXXXXXXXXX")
            return cleaned
        return phone

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(
                f'Максимальный размер файла {filesizeformat(settings.MAX_UPLOAD_SIZE)}. '
                f'Ваш файл {filesizeformat(image.size)}'
            )
        return image