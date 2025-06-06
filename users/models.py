from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

def validate_phone(value):
    if not value.startswith('+7'):
        raise ValidationError("Номер должен начинаться с +7")
    if len(value) != 12:
        raise ValidationError("Номер должен содержать 11 цифр после +7")

class User(AbstractUser):
    phone = models.CharField(
        max_length=20,
        validators=[validate_phone],
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text="Формат: +79991234567"
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )

    image = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text="Рекомендуемый размер: 200x200px"
    )

    def get_initials(self):
        initials = ''
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        return initials if initials else self.username[0].upper()

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'без имени'})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']