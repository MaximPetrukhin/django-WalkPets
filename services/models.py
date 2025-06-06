from enum import unique

from django.db import models

# Create your models here.

# services/models.py

class ServicesCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"

class Services(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название услуги")
    image = models.ImageField(
        upload_to="services_media",
        blank=True,  # Разрешаем пустое значение
        null=True,   # Разрешаем NULL в БД
        verbose_name="Изображение"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    short_description = models.TextField(max_length=64, blank=True, verbose_name="Краткое описание")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(
        ServicesCategory,
        on_delete=models.PROTECT,
        verbose_name="Категория"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"