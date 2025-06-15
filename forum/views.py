from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse  # Добавлен reverse
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Category, Topic, Post
from .forms import TopicForm, PostForm
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

class ForumIndexView(ListView):
    model = Topic
    template_name = 'forum/forum_index.html'
    context_object_name = 'latest_topics'

    def get_queryset(self):
        return Topic.objects.all().order_by('-created_at')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            topics_count=Count('topics')
        ).all()
        context['top_users'] = User.objects.annotate(
            topics_count=Count('topics')
        ).order_by('-topics_count')[:5]
        return context

class CategoryTopicsView(ListView):
    model = Topic
    template_name = 'forum/category_topics.html'
    context_object_name = 'topics'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Topic.objects.filter(category=self.category).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class TopicDetailView(DetailView):
    model = Topic
    template_name = 'forum/topic_detail.html'
    context_object_name = 'topic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')

        self.object = self.get_object()
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.topic = self.object
            post.save()
            return redirect('forum:topic_detail', pk=self.object.pk)

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user.is_authenticated and request.user == self.object.author:
            return response
        self.object.views += 1
        self.object.save()
        return response

class CreateTopicView(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    template_name = 'forum/create_topic.html'
    success_url = reverse_lazy('forum:forum_index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('forum:topic_detail', kwargs={'pk': self.kwargs['pk']})

class AllTopicsView(ListView):
    model = Topic
    template_name = 'forum/all_topics.html'
    context_object_name = 'topics'
    paginate_by = 10  # Можно настроить пагинацию

    def get_queryset(self):
        return Topic.objects.all().order_by('-created_at')

@require_POST
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.author or request.user.is_superuser:
        topic_id = post.topic.id  # Сохраняем ID темы перед удалением
        post.delete()
        messages.success(request, 'Пост успешно удалён.')
        return redirect('forum:topic_detail', pk=topic_id)
    else:
        messages.error(request, 'У вас нет прав на удаление этого поста.')
        return redirect('forum:topic_detail', pk=post.topic.id)

def like_topic(request, pk):
    try:
        topic = get_object_or_404(Topic, pk=pk)
        if request.user in topic.likes.all():
            topic.likes.remove(request.user)
            liked = False
        else:
            topic.likes.add(request.user)
            liked = True
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': topic.likes.count()  # Исправлено с total_likes()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)