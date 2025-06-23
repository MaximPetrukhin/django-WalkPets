from django.contrib import admin
from services.models import Services, ServicesCategory, Walker
from users.models import Review



@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Walker)
class WalkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'experience', 'rating', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'phone')
    actions = ['approve_walkers']

    def approve_walkers(self, request, queryset):
        queryset.update(status='approved')
    approve_walkers.short_description = "Одобрить выбранных выгульщиков"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'review_type', 'walker', 'rating', 'created_at')
    list_filter = ('review_type', 'rating')
    search_fields = ('author__username', 'text')

# @admin.register(ServicesCategory)
# class ServicesCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'description')