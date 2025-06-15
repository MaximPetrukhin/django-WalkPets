from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.safestring import mark_safe
import re
from .models import Review


User = get_user_model()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв здесь...'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'type': 'number'
            })
        }
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка (1-5 звезд)'
        }


class AvatarWidget(forms.ClearableFileInput):
    """Кастомный виджет для загрузки аватара с ограничениями"""
    template_name = 'templates/widgets/avatar_widget.html'

    def __init__(self, attrs=None):
        default_attrs = {
            'accept': 'image/jpeg, image/png, image/webp',
            'class': 'avatar-file-input',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class UserLoginForm(AuthenticationForm):
    """Форма входа с запоминанием пользователя"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control py-3',
            'placeholder': 'Введите имя пользователя',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-3',
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        initial=True
    )

class UserRegistrationForm(UserCreationForm):
    """Форма регистрации с дополнительной валидацией email"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control py-3',
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
                'class': 'form-control py-3',
                'placeholder': 'Введите имя пользователя',
                'autocomplete': 'username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control py-3',
                'placeholder': 'Введите пароль',
                'autocomplete': 'new-password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control py-3',
                'placeholder': 'Подтвердите пароль',
                'autocomplete': 'new-password'
            }),
        }

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

class UserProfileForm(UserChangeForm):
    """Форма редактирования профиля с кастомными полями"""
    email = forms.EmailField(
        disabled=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control py-2',
            'readonly': True,
            'autocomplete': 'email'
        })
    )

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
            'image': AvatarWidget()
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        # Если поле пустое, возвращаем None
        return birth_date if birth_date else None

    def save(self, commit=True):
        user = super().save(commit=False)
        # Явно сохраняем дату рождения
        user.birth_date = self.cleaned_data['birth_date']
        if commit:
            user.save()
        return user


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.birth_date:
            self.initial['birth_date'] = self.instance.birth_date.strftime('%Y-%m-%d')
        self.fields['email'].initial = self.instance.email
        self.fields['password'].help_text = ''
        self.fields['password'].widget = forms.HiddenInput()

    def clean_phone(self):
        """Валидация номера телефона"""
        phone = self.cleaned_data.get('phone')
        if phone:
            cleaned = re.sub(r'[^\d+]', '', phone)
            if not cleaned.startswith('+7') or len(cleaned) != 12:
                raise ValidationError("Номер должен быть в формате +7XXXXXXXXXX")
            return cleaned
        return phone

    def clean_image(self):
        """Проверка размера загружаемого изображения"""
        image = self.cleaned_data.get('image')
        if image and image.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(
                f'Максимальный размер файла {filesizeformat(settings.MAX_UPLOAD_SIZE)}. '
                f'Ваш файл {filesizeformat(image.size)}'
            )
        return image