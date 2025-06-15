from django.urls import path
from .views import (
    ForumIndexView,
    CategoryTopicsView,
    TopicDetailView,
    CreateTopicView,
    CreatePostView,
    like_topic,
    AllTopicsView,
    delete_post  # Добавлен новый импорт
)

app_name = 'forum'

urlpatterns = [
    path('all-topics/', AllTopicsView.as_view(), name='all_topics'),
    path('', ForumIndexView.as_view(), name='forum_index'),
    path('category/<slug:slug>/', CategoryTopicsView.as_view(), name='category_topics'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('topic/new/', CreateTopicView.as_view(), name='create_topic'),
    path('topic/<int:pk>/post/', CreatePostView.as_view(), name='create_post'),
    path('topic/<int:pk>/like/', like_topic, name='like_topic'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),  # Новый путь
]