from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название региона")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")

    def __str__(self):
        return self.name


class PetFriendlyPlaceSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Регион")
    name = models.CharField(max_length=100, verbose_name="Название места")
    description = models.TextField(verbose_name="Описание")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    photo = models.ImageField(upload_to='place_photos/', verbose_name="Фото места")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class PetFriendlyPlace(models.Model):
    submission = models.OneToOneField(
        PetFriendlyPlaceSubmission,
        on_delete=models.CASCADE,
        verbose_name="Заявка",
        related_name='approved_place'
    )
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.submission.name
