document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Подсветка активной категории
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');
    if (category) {
        document.querySelectorAll('.category-item').forEach(item => {
            if (item.textContent.toLowerCase().includes(category.toLowerCase())) {
                item.style.borderLeft = '4px solid #4a7f6b';
                item.style.backgroundColor = '#f0f5f2';
            }
        });
    }

    // Инициализация tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Обработка лайков
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const topicId = this.dataset.topicId;
            const likeCount = this.querySelector('.like-count');

            fetch(`/forum/topic/${topicId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                likeCount.textContent = data.likes_count;
                this.classList.toggle('liked', data.liked);

                if (data.liked) {
                    this.querySelector('i').classList.add('bi-heart-fill');
                    this.querySelector('i').classList.remove('bi-heart');
                } else {
                    this.querySelector('i').classList.add('bi-heart');
                    this.querySelector('i').classList.remove('bi-heart-fill');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});