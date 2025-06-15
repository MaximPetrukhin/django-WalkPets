document.addEventListener('DOMContentLoaded', function() {
    const roomId = {{ room.id|default:0 }};

    // Инициализация только если мы на странице комнаты
    if (roomId) {
        initChatSocket(roomId);
        initEmojiPicker();
        initUIElements();
    }

    // Инициализация для страницы создания чата
    if (document.getElementById('new-chat-form')) {
        initCreateChatForm();
    }
});

function initChatSocket(roomId) {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const chatSocket = new WebSocket(
        protocol + window.location.host +
        '/ws/chat/' + roomId + '/'
    );

    const messageInput = document.getElementById('chat-message-input');
    const messageSubmit = document.getElementById('chat-message-submit');
    const messagesContainer = document.getElementById('chat-messages');

    // Прокрутка к последнему сообщению при загрузке
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    chatSocket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);
            const isCurrentUser = data.user_id == {{ request.user.id }};
            const timestamp = new Date(data.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });

            const messageElement = document.createElement('div');
            messageElement.className = `message ${isCurrentUser ? 'sent' : 'received'}`;
            messageElement.innerHTML = `
                <div class="message-header">
                    <div class="message-sender">${isCurrentUser ? 'Вы' : data.username}</div>
                    <div class="message-time">${timestamp}</div>
                </div>
                <div class="message-content">${data.message}</div>
            `;

            messagesContainer.appendChild(messageElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } catch (error) {
            console.error('Ошибка обработки сообщения:', error);
        }
    };

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'message': message,
                'room_id': roomId
            }));
            messageInput.value = '';
        }
    }

    // Обработчики событий
    messageSubmit.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Обработка ошибок
    chatSocket.onerror = function(error) {
        console.error('WebSocket ошибка:', error);
        showAlert('Ошибка соединения. Пожалуйста, обновите страницу.', 'danger');
    };

    chatSocket.onclose = function(e) {
        console.log('WebSocket соединение закрыто:', e.reason);
        setTimeout(() => {
            showAlert('Соединение прервано. Пытаемся переподключиться...', 'warning');
            setTimeout(() => location.reload(), 3000);
        }, 1000);
    };
}

// Вспомогательная функция для показа уведомлений
function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.prepend(alert);

    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 150);
    }, 5000);
}

// Остальные функции (initEmojiPicker, initUIElements, initCreateChatForm)
// остаются такими же, как в вашем файле, но с добавлением обработки ошибок

async function initEmojiPicker() {
    const emojiPickerBtn = document.getElementById('emoji-picker-btn');
    if (!emojiPickerBtn) return;

    emojiPickerBtn.addEventListener('click', async function(e) {
        e.stopPropagation();

        if (window.emojiPicker) {
            window.emojiPicker.toggle();
            return;
        }

        const { Picker } = await import('https://cdn.jsdelivr.net/npm/@emoji-mart/react');
        const input = document.getElementById('chat-message-input');

        window.emojiPicker = new Picker({
            parent: emojiPickerBtn,
            onEmojiSelect: (emoji) => {
                input.value += emoji.native;
                input.focus();
            },
            position: 'top-start',
            theme: 'light',
            previewPosition: 'none',
            dynamicWidth: true
        });

        document.addEventListener('click', function(e) {
            if (!emojiPickerBtn.contains(e.target)) {
                window.emojiPicker?.hide();
            }
        });
    });
}

function initUIElements() {
    // Управление списком участников
    const participantsToggle = document.getElementById('participants-toggle');
    const participantsDropdown = document.getElementById('participants-dropdown');

    if (participantsToggle && participantsDropdown) {
        participantsToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            participantsDropdown.style.display =
                participantsDropdown.style.display === 'block' ? 'none' : 'block';
        });

        document.addEventListener('click', function() {
            participantsDropdown.style.display = 'none';
        });
    }

    // Кнопка создания нового чата
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', function() {
            window.location.href = "{% url 'chat:create_room' %}";
        });
    }
}

function initCreateChatForm() {
    const form = document.getElementById('new-chat-form');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="loading-spinner"></div> Создание...';

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert(data.error || 'Ошибка при создании чата');
            }
        } catch (error) {
            alert('Ошибка сети: ' + error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}