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
BUTTON_FEEDBACK = "Оставить отзыв🧋"
BUTTON_MENU = "🍹 Меню"
BUTTON_VACANCIES = "💼 Вакансии"
BUTTON_COOPERATION = "🤝 Сотрудничество"
BUTTON_SUGGESTIONS = "💡 Предложения"
BUTTON_BACK = "↩️ Назад"

# Кнопки второго уровня
BUTTON_BUY_FRANCHISE = "🏪 Купить франшизу"
BUTTON_QUALITY = "Качество напитка"
BUTTON_SERVICE = "Качество обслуживания"
BUTTON_OTHER_QUESTION = "❓ Другой вопрос"
BUTTON_SEND_FEEDBACK = "✍️ Отправить отзыв"
BUTTON_SEND_SUGGESTION = "📝 Отправить предложение"

# Кнопки локаций
BUTTON_DEGTYAREV = "Дегтярев"
BUTTON_CITYMALL = "Сити Молл"

# Кнопки вакансий
BUTTON_SEND_RESUME = "📝 Отправить резюме"
BUTTON_CONTACT_ADMIN = "👤 Связаться с администратором"

# Кнопки админ-панели
ADMIN_BUTTON_BROADCAST = "📢 Рассылка"
ADMIN_BUTTON_USERS = "👥 Список пользователей"
ADMIN_BUTTON_CONFIRM = "✅ Подтвердить"
ADMIN_BUTTON_CANCEL = "❌ Отменить"
ADMIN_BUTTON_REPLY = "Ответить"

# Приветственные сообщения
INITIAL_MESSAGE = """Привет, это команда BIBITI мы создали 
бота чтобы помочь вам по всем вопросам."""

WELCOME_MESSAGE = "Выберите интересующий вас раздел:"

# Сообщения для оценки
SELECT_LOCATION = "Выберите адрес:"
RATE_DRINK = "Понравился ли Вам напиток?"
RATE_SERVICE = "Понравилось ли Вам обслуживание?"
RATE_QUALITY = "Оцените качество напитка от 1 до 5 (отправьте цифру):"

# Сообщения благодарности
THANKS_HIGH_RATING = """Команда BIBITI рада, что вы выбрали именно нас,
спасибо за доверие! 🤍"""
THANKS_QUALITY_5 = "Спасибо что выбрали нас! Обращайтесь, если будут вопросы."
THANKS_SERVICE_5 = "Спасибо за оценку! Если есть вопросы, вы можете обратиться к нашему Менеджеру ВВТ."

# Сообщения для обратной связи
FEEDBACK_REQUEST = "Пожалуйста напишите нам, что именно нам следует улучшить?"
FEEDBACK_QUALITY_REQUEST = "Мы хотим стать лучше. Пожалуйста, напишите ваши замечания:"
FEEDBACK_SERVICE_REQUEST = "Пожалуйста, расскажите, что именно вам не понравилось. Мы постараемся это исправить:"
FEEDBACK_THANKS = "Спасибо за ваш отзыв! Мы обязательно учтем ваше мнение."
THANKS_FEEDBACK = "Спасибо за ваш отзыв! Мы обязательно его рассмотрим."

# Сообщения для сотрудничества
COOPERATION_CHOICE = """Выберите интересующий вас вариант сотрудничества:"""
COOPERATION_REQUEST = """Пожалуйста, опишите ваше предложение или вопрос.
Для прямой связи с администратором, напишите: @rfatyhov"""

# Сообщения для предложений
SUGGESTIONS_REQUEST = """Поделитесь вашими идеями и предложениями.
Для связи с администратором, напишите: @rfatyhov"""
THANKS_SUGGESTIONS = "Спасибо за ваши предложения! Мы обязательно рассмотрим их."

# Сообщения для вакансий
VACANCIES_DESCRIPTION = """У нас открыты следующие вакансии:
- Бариста
- Администратор

Требования:
- Опыт работы от 1 года
- Ответственность
- Коммуникабельность

Условия:
- График 2/2
- Достойная оплата
- Дружный коллектив

Для связи с администратором, напишите: @rfatyhov
"""
RESUME_REQUEST = "Пожалуйста, отправьте ваше краткое резюме:"

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
ADMIN_NEW_TICKET = """Новое обращение #{ticket_id}
Тип: {feedback_type}
От: {first_name} {last_name} (@{username})
Сообщение: {message}"""

# Сообщения об ошибках
ERROR_BROADCAST_TEXT_NOT_FOUND = "Ошибка: текст рассылки не найден"
ERROR_GENERAL = """Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с администратором: @rfatyhov"""
ERROR_INVALID_RATING = "Пожалуйста, отправьте число от 1 до 5"
