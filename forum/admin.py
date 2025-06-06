from django.contrib import admin

from django.contrib import admin
from .models import Category, Topic, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'views')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'topic', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)