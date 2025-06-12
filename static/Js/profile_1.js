document.addEventListener('DOMContentLoaded', function() {
    // Инициализация tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Предпросмотр аватара
    const avatarInput = document.querySelector('input[name="image"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const avatarImg = document.querySelector('.avatar-img');
                    if (avatarImg) {
                        avatarImg.src = event.target.result;
                    } else {
                        const placeholder = document.querySelector('.avatar-placeholder');
                        if (placeholder) {
                            placeholder.innerHTML = `<img src="${event.target.result}" class="avatar-img" alt="Аватар">`;
                        }
                    }
                };
                reader.readAsDataURL(e.target.files[0]);

                // Авто-отправка формы
                this.closest('form').submit();
            }
        });
    }

    // Маска для телефона
    const phoneInput = document.querySelector('input[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 1) {
                value = '+7' + value.substring(1);
            }
            this.value = value;
        });
    }
});