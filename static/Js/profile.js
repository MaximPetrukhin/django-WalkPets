document.addEventListener('DOMContentLoaded', function() {
    // Инициализация элементов
    const avatarInput = document.getElementById('avatar-input');
    const deleteBtn = document.getElementById('delete-avatar');
    const phoneInput = document.getElementById('id_phone');

    // Маска для телефона
    if (phoneInput) {
        Inputmask({
            mask: '+7 (999) 999-99-99',
            placeholder: '_',
            showMaskOnHover: false,
            showMaskOnFocus: true
        }).mask(phoneInput);
    }

    // Обработка загрузки аватара
    if (avatarInput) {
        avatarInput.addEventListener('change', handleAvatarUpload);
    }

    // Обработка удаления аватара
    if (deleteBtn) {
        deleteBtn.addEventListener('click', handleAvatarDelete);
    }

    // Функция загрузки аватара
    function handleAvatarUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Проверка типа файла
        if (!file.type.match('image.*')) {
            showMessage('Пожалуйста, выберите файл изображения', 'error');
            return;
        }

        // Проверка размера файла (макс. 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showMessage('Размер файла не должен превышать 5MB', 'error');
            return;
        }

        // Предпросмотр
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('avatar-preview');
            if (preview.tagName === 'IMG') {
                preview.src = e.target.result;
            } else {
                const img = document.createElement('img');
                img.id = 'avatar-preview';
                img.className = 'avatar-image';
                img.src = e.target.result;
                img.alt = 'Аватар пользователя';
                preview.replaceWith(img);
            }
        };
        reader.readAsDataURL(file);

        // AJAX-загрузка
        const formData = new FormData();
        formData.append('image', file);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        fetch("{% url 'users:upload_avatar' %}", {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                showMessage('Аватар успешно обновлен', 'success');
                // Показываем кнопку удаления
                if (deleteBtn) deleteBtn.style.display = 'block';
                // Обновляем страницу через 1 секунду
                setTimeout(() => window.location.reload(), 1000);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки:', error);
            showMessage('Ошибка загрузки: ' + error.message, 'error');
        });
    }

    // Функция удаления аватара
    function handleAvatarDelete() {
        if (!confirm('Вы уверены, что хотите удалить аватар?')) return;

        fetch("{% url 'users:delete_avatar' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const preview = document.getElementById('avatar-preview');
                if (preview.tagName === 'IMG') {
                    const placeholder = document.createElement('div');
                    placeholder.id = 'avatar-preview';
                    placeholder.className = 'avatar-placeholder';
                    placeholder.textContent =
                        '{{ user.first_name|first|upper }}{{ user.last_name|first|upper }}';
                    preview.replaceWith(placeholder);
                }
                if (deleteBtn) deleteBtn.style.display = 'none';
                showMessage('Аватар удален', 'success');
            } else {
                throw new Error(data.error || 'Не удалось удалить аватар');
            }
        })
        .catch(error => {
            console.error('Ошибка удаления:', error);
            showMessage('Ошибка: ' + error.message, 'error');
        });
    }

    // Функция показа сообщений
    function showMessage(text, type) {
        const messagesDiv = document.querySelector('.messages') || createMessagesContainer();
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = text;
        messagesDiv.appendChild(messageDiv);

        // Автоудаление через 5 секунд
        setTimeout(() => {
            messageDiv.remove();
            if (messagesDiv.children.length === 0) {
                messagesDiv.remove();
            }
        }, 5000);
    }

    function createMessagesContainer() {
        const container = document.createElement('div');
        container.className = 'messages';
        document.body.prepend(container);
        return container;
    }
});