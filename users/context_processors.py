from .models import Review

def top_reviews(request):
    top_reviews = Review.objects.filter(
        is_published=True,
        rating__gte=4
    ).order_by('-created_at')[:5]
    return {'top_reviews': top_reviews}