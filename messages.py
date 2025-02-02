# Команды
CMD_START = "start"
CMD_QUALITY = "quality"
CMD_COOPERATION = "cooperation"
CMD_SUGGESTIONS = "suggestions"
CMD_SERVICE = "service"
CMD_ADMIN = "admin"
CMD_BROADCAST = "broadcast"
CMD_USERS = "users"
CMD_BACK = "back"
CMD_FRANCHISE = "franchise"
CMD_OTHER = "other"

# Кнопки главного меню
BUTTON_QUALITY = "🌟 Качество"
BUTTON_COOPERATION = "🤝 Сотрудничество"
BUTTON_SUGGESTIONS = "💡 Ваши предложения"
BUTTON_SERVICE = "👨‍💼 Обслуживание"
BUTTON_BACK = "« Назад"

# Кнопки второго уровня
BUTTON_BUY_FRANCHISE = "🏪 Купить франшизу"
BUTTON_OTHER_QUESTION = "❓ Другой вопрос"
BUTTON_SEND_FEEDBACK = "✍️ Отправить отзыв"
BUTTON_SEND_SUGGESTION = "📝 Отправить предложение"

# Кнопки админ-панели
ADMIN_BUTTON_BROADCAST = "📢 Сделать рассылку"
ADMIN_BUTTON_USERS = "👥 Список пользователей"
ADMIN_BUTTON_CONFIRM = "✅ Подтвердить"
ADMIN_BUTTON_CANCEL = "❌ Отменить"
ADMIN_BUTTON_REPLY = "↩️ Ответить"

# Приветственные сообщения
WELCOME_MESSAGE = "Добро пожаловать! Выберите интересующий вас раздел:"

# Сообщения для оценки
RATE_QUALITY = "Оцените качество напитка от 1 до 5 (отправьте цифру):"
RATE_SERVICE = "Оцените обслуживание от 1 до 5 (отправьте цифру):"

# Сообщения благодарности
THANKS_QUALITY_5 = "Спасибо что выбрали нас! Обращайтесь, если будут вопросы."
THANKS_SERVICE_5 = "Спасибо за оценку! Если есть вопросы, вы можете обратиться к нашему Менеджеру ВВТ."

# Сообщения для обратной связи
FEEDBACK_QUALITY_REQUEST = "Мы хотим стать лучше. Пожалуйста, напишите ваши замечания:"
FEEDBACK_SERVICE_REQUEST = "Пожалуйста, расскажите, что именно вам не понравилось. Мы постараемся это исправить:"
FEEDBACK_THANKS = "Спасибо за ваш отзыв! Мы обязательно рассмотрим его."

# Сообщения для сотрудничества
COOPERATION_CHOICE = "Выберите тип сотрудничества:"
COOPERATION_REQUEST = "Пожалуйста, опишите ваш запрос:"

# Сообщения для предложений
SUGGESTIONS_REQUEST = "Отправьте ваше предложение об улучшении:"

# Административные сообщения
ADMIN_NO_RIGHTS = "У вас нет прав для этой команды."
ADMIN_MENU_TITLE = "Панель администратора:"
ADMIN_BROADCAST_USAGE = "Введите текст сообщения для рассылки:"
ADMIN_BROADCAST_CONFIRM = "Подтвердите отправку рассылки:\n\n{text}"
ADMIN_BROADCAST_COMPLETE = "Рассылка завершена\nУспешно: {success}\nОшибок: {fail}"
ADMIN_BROADCAST_CANCEL = "Рассылка отменена"
ADMIN_USERS_LIST_HEADER = "Список пользователей сохранен в файл users_list.txt"
ADMIN_USER_INFO = """ID: {user_id}
Username: @{username}
Имя: {first_name} {last_name}
"""
ADMIN_REPLY_REQUEST = "Введите ответ на обращение {ticket_id}:"
ADMIN_REPLY_SENT = "✅ Ответ на обращение {ticket_id} отправлен"
ADMIN_REPLY_FAILED = "❌ Не удалось отправить ответ на обращение {ticket_id}"

# Сообщения для пользователя
USER_REPLY_RECEIVED = "📨 Ответ на ваше обращение {ticket_id}:\n\n{reply}"

# Формат заявки для админа
ADMIN_NEW_TICKET = """Новая заявка {ticket_id}
Тип: {feedback_type}
От: {first_name} {last_name} (@{username})
Сообщение: {message}"""

# Сообщения об ошибках
ERROR_BROADCAST_TEXT_NOT_FOUND = "Ошибка: текст рассылки не найден"
ERROR_GENERAL = "Произошла ошибка. Пожалуйста, попробуйте позже."
ERROR_INVALID_RATING = "Пожалуйста, отправьте число от 1 до 5"
