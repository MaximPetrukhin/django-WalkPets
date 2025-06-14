from django.contrib import admin
from .models import Region, PetFriendlyPlaceSubmission, PetFriendlyPlace

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')

@admin.register(PetFriendlyPlaceSubmission)
class PetFriendlyPlaceSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'region', 'status', 'created_at')
    list_filter = ('status', 'region')
    actions = ['approve_submissions']

    def approve_submissions(self, request, queryset):
        for submission in queryset:
            # Логика создания точки на карте
            pass
        self.message_user(request, f"{queryset.count()} заявок одобрено")
    approve_submissions.short_description = "Одобрить выбранные заявки"

@admin.register(PetFriendlyPlace)
class PetFriendlyPlaceAdmin(admin.ModelAdmin):
    list_display = ('submission', 'latitude', 'longitude', 'added_at')