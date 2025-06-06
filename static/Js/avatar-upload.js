class AvatarUploader {
    constructor() {
        this.modal = document.getElementById('delete-modal');
        this.initEvents();
    }

    initEvents() {
        const deleteBtn = document.getElementById('delete-avatar');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.showModal());
        }

        document.getElementById('cancel-delete').addEventListener('click', () => this.hideModal());
        document.querySelector('.modal-close').addEventListener('click', () => this.hideModal());
        document.getElementById('confirm-delete').addEventListener('click', () => this.deleteAvatar());
    }

    showModal() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hideModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    async deleteAvatar() {
        try {
            const response = await fetch(document.getElementById('delete-avatar').dataset.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Ошибка сервера');

            const data = await response.json();

            if (data.success) {
                this.hideModal();
                window.location.reload();
            } else {
                throw new Error(data.error || 'Ошибка удаления');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            this.hideModal();
        }
    }

    // Получение CSRF токена
    getCookie(name) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    // Показать уведомление
    showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    // Обработка загрузки аватара
    handleAvatarChange(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Валидация файла
        const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            this.showToast('Пожалуйста, выберите изображение (JPEG, PNG, WebP)', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            this.showToast('Размер файла не должен превышать 5MB', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('image', file);
        formData.append('csrfmiddlewaretoken', this.csrfToken);

        this.uploadAvatar(formData);
    }

    // Загрузка аватара на сервер
    async uploadAvatar(formData) {
        try {
            const response = await fetch(document.getElementById('avatar-form').dataset.url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Ошибка сервера');

            const data = await response.json();

            if (data.status === 'success') {
                this.showToast('Аватар успешно обновлен');
                this.updateAvatarPreview(data.avatar_url);
                this.toggleDeleteButton(true);
            } else {
                throw new Error(data.message || 'Ошибка загрузки');
            }
        } catch (error) {
            this.showToast('Ошибка: ' + error.message, 'error');
            console.error('Ошибка загрузки:', error);
        }
    }

    // Обновление превью аватара
    updateAvatarPreview(avatarUrl) {
        const avatarPreview = document.getElementById('avatar-preview');
        if (!avatarPreview) return;

        if (avatarPreview.tagName === 'IMG') {
            avatarPreview.src = avatarUrl + '?t=' + Date.now();
        } else {
            const img = document.createElement('img');
            img.id = 'avatar-preview';
            img.src = avatarUrl;
            img.alt = 'Аватар пользователя';
            img.className = 'avatar-image';
            avatarPreview.replaceWith(img);
        }
    }

    // Переключение видимости кнопки удаления
    toggleDeleteButton(show) {
        const deleteBtn = document.getElementById('delete-avatar');
        if (deleteBtn) {
            deleteBtn.style.display = show ? 'block' : 'none';
        }
    }

    // Настройка модального окна
    setupModal() {
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeModal();
            }
        });
    }

    // Открытие модального окна
    openModal() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Закрытие модального окна
    closeModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Обработка удаления аватара
    async handleDeleteAvatar() {
        this.openModal();

        return new Promise((resolve) => {
            const confirmHandler = async () => {
                try {
                    const response = await fetch(document.getElementById('delete-avatar').dataset.url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': this.csrfToken,
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept': 'application/json'
                        }
                    });

                    if (!response.ok) throw new Error('Ошибка сервера');

                    const data = await response.json();

                    if (data.success) {
                        this.showToast(data.message || 'Аватар удален');
                        setTimeout(() => window.location.reload(), 1500);
                        resolve(true);
                    } else {
                        throw new Error(data.error || 'Ошибка удаления');
                    }
                } catch (error) {
                    this.showToast('Ошибка: ' + error.message, 'error');
                    console.error('Ошибка удаления:', error);
                    resolve(false);
                } finally {
                    this.cleanupModalHandlers(confirmHandler, cancelHandler);
                    this.closeModal();
                }
            };

            const cancelHandler = () => {
                resolve(false);
                this.cleanupModalHandlers(confirmHandler, cancelHandler);
                this.closeModal();
            };

            document.getElementById('confirm-delete').addEventListener('click', confirmHandler);
            document.getElementById('cancel-delete').addEventListener('click', cancelHandler);
            document.querySelector('.modal-close').addEventListener('click', cancelHandler);
        });
    }

    // Очистка обработчиков модального окна
    cleanupModalHandlers(confirmHandler, cancelHandler) {
        document.getElementById('confirm-delete').removeEventListener('click', confirmHandler);
        document.getElementById('cancel-delete').removeEventListener('click', cancelHandler);
        document.querySelector('.modal-close').removeEventListener('click', cancelHandler);
    }

    // Восстановление плейсхолдера
    restorePlaceholder(initials) {
        const preview = document.getElementById('avatar-preview');
        if (!preview) return;

        const placeholder = document.createElement('div');
        placeholder.id = 'avatar-preview';
        placeholder.className = 'avatar-placeholder';
        placeholder.textContent = initials || '??';
        preview.replaceWith(placeholder);
    }

    // Инициализация событий
    initEvents() {
        const avatarInput = document.getElementById('avatar-input');
        const deleteBtn = document.getElementById('delete-avatar');

        if (avatarInput) {
            avatarInput.addEventListener('change', this.handleAvatarChange.bind(this));
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.handleDeleteAvatar());
        }

        // Инициализация маски телефона
        const phoneInput = document.getElementById('id_phone');
        if (phoneInput && typeof Inputmask !== 'undefined') {
            Inputmask({
                mask: '+7 (999) 999-99-99',
                placeholder: '_',
                showMaskOnHover: false
            }).mask(phoneInput);
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new AvatarUploader();
});