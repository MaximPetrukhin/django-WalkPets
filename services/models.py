from django.db import models
from django.conf import settings
from django.db.models import Avg
from users.models import Review


class ServicesCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(
        upload_to="categories_media",
        blank=True,
        null=True,
        verbose_name="Изображение категории"
    )
    slug = models.SlugField(max_length=50, unique=True, verbose_name="URL-адрес")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"


class Services(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название услуги")
    image = models.ImageField(
        upload_to="services_media",
        blank=True,
        null=True,
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


class Walker(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя выгульщика")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    image = models.ImageField(
        upload_to="walkers_media",
        blank=True,
        null=True,
        verbose_name="Фото"
    )

    description = models.TextField(verbose_name="О себе")
    experience = models.PositiveIntegerField(default=0, verbose_name="Опыт работы (лет)")
    rating = models.FloatField(default=5.0, verbose_name="Рейтинг")

    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, null=True, blank=True,
                                verbose_name="Пользователь")

    def update_rating(self):
        """Обновляет рейтинг выгульщика на основе отзывов"""
        result = Review.objects.filter(
            walker=self,
            review_type='walker'
        ).aggregate(avg_rating=Avg('rating'))
        self.rating = round(result['avg_rating'], 1) if result['avg_rating'] else 5.0
        self.save()

    def __str__(self):
        return f'Отзыв от {self.author.username} ({self.rating} звезд)'

    @property
    def stars(self):
        return range(self.rating)

    @property
    def empty_stars(self):
        return range(5 - self.rating)
