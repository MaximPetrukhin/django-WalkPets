class AvatarUploader {
    constructor() {
        this.modal = document.getElementById('delete-modal');
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        this.initEvents();
        this.setupModal();
    }

    initEvents() {
        // Обработчик загрузки аватара
        const avatarInput = document.getElementById('avatar-input');
        if (avatarInput) {
            avatarInput.addEventListener('change', (e) => this.handleAvatarChange(e));
        }

        // Обработчик удаления аватара
        const deleteBtn = document.getElementById('delete-avatar');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.showModal());
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

    setupModal() {
        // Закрытие по клику на оверлей
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });

        // Закрытие по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.hideModal();
            }
        });

        // Обработчики кнопок модального окна
        document.getElementById('confirm-delete').addEventListener('click', () => this.handleDeleteAvatar());
        document.getElementById('cancel-delete').addEventListener('click', () => this.hideModal());
        document.querySelector('.modal-close').addEventListener('click', () => this.hideModal());
    }

    showModal() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hideModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }

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

        this.uploadAvatar(formData);
    }

    async uploadAvatar(formData) {
        try {
            const avatarForm = document.getElementById('avatar-form');
            if (!avatarForm || !avatarForm.dataset.url) {
                throw new Error('Форма загрузки не найдена');
            }

            // Добавляем CSRF токен в FormData
            formData.append('csrfmiddlewaretoken', this.csrfToken);

            const response = await fetch(avatarForm.dataset.url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'include' // Важно для передачи куки
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();
            this.showToast(data.message || 'Аватар успешно обновлен');
            this.updateAvatarPreview(data.avatar_url);
            this.toggleDeleteButton(true);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            this.showToast('Ошибка: ' + error.message, 'error');
        }
    }

    async handleDeleteAvatar() {
        try {
            const deleteBtn = document.getElementById('delete-avatar');
            if (!deleteBtn || !deleteBtn.dataset.url) {
                throw new Error('Кнопка удаления или URL не найдены');
            }

            const response = await fetch(deleteBtn.dataset.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();
            this.showToast(data.message || 'Аватар удален');
            this.restorePlaceholder(data.initials);
            this.toggleDeleteButton(false);
            this.hideModal();
        } catch (error) {
            console.error('Ошибка удаления:', error);
            this.showToast('Ошибка: ' + error.message, 'error');
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new AvatarUploader();
});