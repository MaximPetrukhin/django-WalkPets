document.addEventListener('DOMContentLoaded', function() {
    // Маска для телефона
    const phoneInput = document.querySelector('input[name="phone"]');

    phoneInput.addEventListener('input', function(e) {
        // Удаляем все нецифровые символы
        let value = this.value.replace(/\D/g, '');

        // Форматируем номер
        if (value.length > 0) {
            value = '+7' + value.substring(1); // Заменяем первую цифру на +7
            if (value.length > 2) {
                value = value.substring(0, 2) + '(' + value.substring(2);
            }
            if (value.length > 6) {
                value = value.substring(0, 6) + ')' + value.substring(6);
            }
            if (value.length > 10) {
                value = value.substring(0, 10) + '-' + value.substring(10);
            }
            if (value.length > 13) {
                value = value.substring(0, 13) + '-' + value.substring(13);
            }
            if (value.length > 16) {
                value = value.substring(0, 16);
            }
        }

        this.value = value;
    });

    // При загрузке страницы форматируем существующий номер
    if (phoneInput.value) {
        phoneInput.dispatchEvent(new Event('input'));
    }
});