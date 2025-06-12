from django.db import models

class PetFriendlyPlace(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название места")
    description = models.TextField(verbose_name="Описание")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name