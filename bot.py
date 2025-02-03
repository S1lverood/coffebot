import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InputMediaPhoto, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from telegram.error import TelegramError
import messages as msg
import uuid
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# States
MAIN_MENU, LOCATION_SELECTION, RATING_DRINKS, RATING_SERVICE, FEEDBACK, WAITING_RESUME, COOPERATION_MENU, WAITING_BROADCAST, WAITING_REPLY = range(9)

# Admin ID from environment
ADMIN_ID = os.getenv('ADMIN_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# File paths
USERS_FILE = 'users_data.json'
USERS_LIST_FILE = 'users.txt'
MENU_PHOTOS = ['menu1.jpg', 'menu2.jpg', 'menu3.jpg']

# Store user data
users_data = {}
feedbacks = {}  # Глобальное хранилище для обращений
feedback_counter = 0
active_tickets = {}

def load_users_data():
    """Load users data from file"""
    global users_data
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading users data: {e}")

def save_users_data():
    """Save users data to file"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving users data: {e}")

def save_users_list():
    """Save users list to text file"""
    try:
        with open(USERS_LIST_FILE, 'w', encoding='utf-8') as f:
            f.write("Список пользователей\n")
            f.write("==================\n\n")
            for user_id, user_info in users_data.items():
                f.write(msg.ADMIN_USER_INFO.format(
                    user_id=user_id,
                    username=user_info['username'],
                    first_name=user_info['first_name'],
                    last_name=user_info['last_name']
                ))
                f.write("\n" + "="*40 + "\n\n")
    except Exception as e:
        logger.error(f"Error saving users list: {e}")

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return str(user_id) == ADMIN_ID

def get_main_menu_keyboard(is_admin_user: bool = False):
    """Get main menu keyboard"""
    keyboard = [
        [msg.BUTTON_FEEDBACK],
        [msg.BUTTON_MENU, msg.BUTTON_VACANCIES],
        [msg.BUTTON_COOPERATION, msg.BUTTON_SUGGESTIONS]
    ]
    if is_admin_user:
        keyboard.append([msg.ADMIN_BUTTON_BROADCAST, msg.ADMIN_BUTTON_USERS])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_location_keyboard():
    """Get location selection keyboard"""
    keyboard = [
        [KeyboardButton(get_location_button_text("Дегтярев"))],
        [KeyboardButton(get_location_button_text("Сити Молл"))],
        [KeyboardButton(msg.BUTTON_BACK)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_rating_keyboard():
    """Get rating inline keyboard"""
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f'rate_{i}') for i in range(1, 6)],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_vacancies_keyboard():
    """Get vacancies keyboard"""
    keyboard = [
        [msg.BUTTON_SEND_RESUME],
        [msg.BUTTON_CONTACT_ADMIN],
        [msg.BUTTON_BACK]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cooperation_keyboard():
    """Get cooperation menu keyboard"""
    keyboard = [
        [msg.BUTTON_BUY_FRANCHISE],
        [msg.BUTTON_OTHER_QUESTION],
        [msg.BUTTON_BACK]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def save_user_data(user):
    """Save user data to storage"""
    global users_data
    
    # Ensure users_data is initialized
    if users_data is None:
        users_data = {}
    
    # Always update user data
    users_data[str(user.id)] = {
        'username': user.username or '',
        'first_name': user.first_name or '',
        'last_name': user.last_name or ''
    }
    
    try:
        save_users_data()
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

def save_feedback(user_id: int, feedback_type: str, text: str) -> str:
    """Save feedback and return feedback ID"""
    feedback_id = str(uuid.uuid4())
    feedbacks[feedback_id] = {
        'user_id': user_id,
        'type': feedback_type,
        'text': text,
        'timestamp': datetime.now().isoformat()
    }
    return feedback_id

def resize_image(image_path):
    """Resize image to fit Telegram requirements"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get dimensions
            width, height = img.size
            
            # Calculate new dimensions
            max_size = 1280  # Telegram recommended size
            if width > height:
                if width > max_size:
                    ratio = max_size / width
                    new_width = max_size
                    new_height = int(height * ratio)
            else:
                if height > max_size:
                    ratio = max_size / height
                    new_height = max_size
                    new_width = int(width * ratio)
                    
            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            bio = io.BytesIO()
            bio.name = 'image.jpg'
            img.save(bio, 'JPEG')
            bio.seek(0)
            return bio
    except Exception as e:
        logger.error(f"Error resizing image {image_path}: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    try:
        # Проверяем наличие сообщения
        if not update.message:
            logger.error("No message in update")
            return ConversationHandler.END
            
        user = update.message.from_user
        if not user:
            logger.error("No user in message")
            return ConversationHandler.END
            
        try:
            save_user_data(user)
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            # Продолжаем выполнение, так как это не критическая ошибка
        
        # Try to send photo with caption if exists
        welcome_sent = False
        if os.path.exists('welcome.jpg') and os.path.getsize('welcome.jpg') > 0:
            try:
                with open('welcome.jpg', 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=msg.INITIAL_MESSAGE
                    )
                    welcome_sent = True
            except Exception as e:
                logger.error(f"Error sending welcome photo: {e}")
                # Продолжаем выполнение и отправим текстовое сообщение
        
        if not welcome_sent:
            await update.message.reply_text(msg.INITIAL_MESSAGE)
        
        is_admin_user = is_admin(user.id)
        reply_markup = get_main_menu_keyboard(is_admin_user)
        await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
        return MAIN_MENU
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        # Пытаемся отправить сообщение об ошибке, если возможно
        try:
            if update and update.message:
                await update.message.reply_text(msg.ERROR_GENERAL)
        except:
            pass
        return ConversationHandler.END

async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        menu_photos = [
            'menu1.jpg',
            'menu2.jpg',
            'menu3.jpg'
        ]
        
        for photo in menu_photos:
            if os.path.exists(photo):
                resized_photo = resize_image(photo)
                if resized_photo:
                    await update.message.reply_photo(photo=resized_photo)
                else:
                    logging.error(f"Failed to resize photo: {photo}")
            else:
                logging.error(f"Menu photo not found: {photo}")
        
        return MAIN_MENU
            
    except Exception as e:
        logging.error(f"Error sending menu: {e}")
        await update.message.reply_text("Извините, произошла ошибка при отправке меню")
        return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu options"""
    try:
        text = update.message.text

        if text == msg.BUTTON_FEEDBACK:
            reply_markup = get_location_keyboard()
            await update.message.reply_text(msg.SELECT_LOCATION, reply_markup=reply_markup)
            return LOCATION_SELECTION

        elif text == msg.BUTTON_MENU:
            await send_menu(update, context)
            return MAIN_MENU

        elif text == msg.BUTTON_VACANCIES:
            reply_markup = get_vacancies_keyboard()
            await update.message.reply_text(msg.VACANCIES_DESCRIPTION, reply_markup=reply_markup)
            return WAITING_RESUME

        elif text == msg.BUTTON_COOPERATION:
            reply_markup = get_cooperation_keyboard()
            await update.message.reply_text(msg.COOPERATION_CHOICE, reply_markup=reply_markup)
            return COOPERATION_MENU

        elif text == msg.BUTTON_SUGGESTIONS:
            await update.message.reply_text(
                msg.SUGGESTIONS_REQUEST,
                reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
            )
            context.user_data['feedback_type'] = 'suggestion'
            return FEEDBACK

        elif text == msg.ADMIN_BUTTON_BROADCAST and is_admin(update.message.from_user.id):
            await update.message.reply_text(
                msg.ADMIN_BROADCAST_USAGE,
                reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
            )
            return WAITING_BROADCAST

        elif text == msg.ADMIN_BUTTON_USERS and is_admin(update.message.from_user.id):
            save_users_list()
            try:
                with open(USERS_LIST_FILE, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename='users_list.txt',
                        caption=msg.ADMIN_USERS_LIST_HEADER
                    )
            except Exception as e:
                logger.error(f"Error sending users list: {e}")
                await update.message.reply_text(msg.ERROR_GENERAL)
            return MAIN_MENU

        elif text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in main menu handler: {e}")
        await update.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [msg.BUTTON_QUALITY],
        [msg.BUTTON_SERVICE],
        [msg.BUTTON_BACK]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)

async def handle_location_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location selection"""
    try:
        # Extract location name without rating info
        location = update.message.text.split(" (")[0]
        
        if location not in ["Дегтярев", "Сити Молл"]:
            await update.message.reply_text(msg.INVALID_LOCATION)
            return LOCATION_SELECTION

        # Save location in user context
        context.user_data['current_location'] = location
        
        # Create rating keyboard
        keyboard = [[
            InlineKeyboardButton("1", callback_data="rate_drink_1"),
            InlineKeyboardButton("2", callback_data="rate_drink_2"),
            InlineKeyboardButton("3", callback_data="rate_drink_3"),
            InlineKeyboardButton("4", callback_data="rate_drink_4"),
            InlineKeyboardButton("5", callback_data="rate_drink_5"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Оцените качество напитков в {location}:",
            reply_markup=reply_markup
        )
        return RATING_DRINKS
        
    except Exception as e:
        logger.error(f"Error in handle_location_selection: {e}")
        await update.message.reply_text(msg.ERROR_MESSAGE)
        return MAIN_MENU

async def handle_drink_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle drink rating"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Extract rating from callback data
        rating = int(query.data.split('_')[-1])
        location = context.user_data.get('current_location')
        
        # Save drink rating
        user_id = str(query.from_user.id)
        if user_id not in users_data:
            users_data[user_id] = {'ratings': []}
        
        # Find existing rating for this location or create new
        rating_entry = None
        for entry in users_data[user_id].get('ratings', []):
            if entry.get('location') == location:
                rating_entry = entry
                break
                
        if rating_entry is None:
            rating_entry = {'location': location}
            users_data[user_id].setdefault('ratings', []).append(rating_entry)
            
        rating_entry['drink_rating'] = rating
        
        # Save updated data
        save_users_data()
        
        # Create service rating keyboard
        keyboard = [[
            InlineKeyboardButton("1", callback_data="rate_service_1"),
            InlineKeyboardButton("2", callback_data="rate_service_2"),
            InlineKeyboardButton("3", callback_data="rate_service_3"),
            InlineKeyboardButton("4", callback_data="rate_service_4"),
            InlineKeyboardButton("5", callback_data="rate_service_5"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"Оцените качество обслуживания в {location}:",
            reply_markup=reply_markup
        )
        return RATING_SERVICE
        
    except Exception as e:
        logger.error(f"Error in handle_drink_rating: {e}")
        await update.callback_query.message.reply_text(msg.ERROR_MESSAGE)
        return MAIN_MENU

async def handle_service_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service rating"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Extract rating from callback data
        rating = int(query.data.split('_')[-1])
        location = context.user_data.get('current_location')
        
        # Save service rating
        user_id = str(query.from_user.id)
        for entry in users_data[user_id].get('ratings', []):
            if entry.get('location') == location:
                entry['service_rating'] = rating
                # Проверяем комбинацию оценок
                drink_rating = entry.get('drink_rating', 0)
                
                # Если любая из оценок 4 или ниже, запрашиваем обратную связь
                if rating <= 4 or drink_rating <= 4:
                    # Если обе оценки <= 4, спрашиваем про более низкую оценку
                    if rating <= 4 and drink_rating <= 4:
                        if rating < drink_rating:
                            context.user_data['feedback_type'] = 'service_quality'
                            feedback_text = msg.FEEDBACK_SERVICE_REQUEST
                        else:
                            context.user_data['feedback_type'] = 'drink_quality'
                            feedback_text = msg.FEEDBACK_QUALITY_REQUEST
                    else:
                        # Иначе спрашиваем про ту, которая <= 4
                        if rating <= 4:
                            context.user_data['feedback_type'] = 'service_quality'
                            feedback_text = msg.FEEDBACK_SERVICE_REQUEST
                        else:
                            context.user_data['feedback_type'] = 'drink_quality'
                            feedback_text = msg.FEEDBACK_QUALITY_REQUEST
                    
                    await query.edit_message_text(
                        text=feedback_text,
                        reply_markup=None
                    )
                    return FEEDBACK
                break
                
        # Save updated data
        save_users_data()
        
        # Calculate new ratings
        avg_drink, avg_service, total = calculate_location_rating(location)
        
        await query.edit_message_text(
            f"Спасибо за оценку!\n\n"
            f"Текущий рейтинг {location}:\n"
            f"Качество напитков: {avg_drink}/5\n"
            f"Качество обслуживания: {avg_service}/5\n"
            f"Всего оценок: {total}"
        )
        
        # Return to location selection
        await send_location_keyboard(update, context)
        return LOCATION_SELECTION
        
    except Exception as e:
        logger.error(f"Error in handle_service_rating: {e}")
        await update.callback_query.message.reply_text(msg.ERROR_MESSAGE)
        return MAIN_MENU

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feedback text"""
    try:
        feedback_type = context.user_data.get('feedback_type', 'general')
        text = update.message.text

        if text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU

        # Save feedback
        feedback_id = save_feedback(update.message.from_user.id, feedback_type, text)

        # Thank user
        is_admin_user = is_admin(update.message.from_user.id)
        reply_markup = get_main_menu_keyboard(is_admin_user)
        await update.message.reply_text(msg.THANKS_FEEDBACK, reply_markup=reply_markup)

        # Notify admin
        admin_id = ADMIN_ID
        if admin_id:
            feedback_data = feedbacks[feedback_id]
            admin_message = f"""Новое обращение!
Тип: {feedback_type}
Текст: {text}
От: {update.message.from_user.full_name} (@{update.message.from_user.username})
ID: {feedback_id}"""
            
            keyboard = [[InlineKeyboardButton("Ответить", callback_data=f"reply_{feedback_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error sending notification to admin: {e}")

        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in feedback handler: {e}")
        await update.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def handle_cooperation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cooperation menu options"""
    try:
        text = update.message.text

        if text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU
        
        elif text == msg.BUTTON_BUY_FRANCHISE:
            await update.message.reply_text(
                "Для получения информации о франшизе, пожалуйста, опишите ваш запрос:",
                reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
            )
            context.user_data['feedback_type'] = 'franchise'
            return FEEDBACK
            
        elif text == msg.BUTTON_OTHER_QUESTION:
            await update.message.reply_text(
                "Пожалуйста, опишите ваш вопрос:",
                reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
            )
            context.user_data['feedback_type'] = 'cooperation'
            return FEEDBACK

        context.user_data['feedback_type'] = 'cooperation'
        await update.message.reply_text(
            msg.COOPERATION_REQUEST,
            reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
        )
        return FEEDBACK

    except Exception as e:
        logger.error(f"Error in cooperation menu handler: {e}")
        await update.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def handle_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle resume submission"""
    try:
        text = update.message.text
        
        if text == msg.BUTTON_SEND_RESUME:
            await update.message.reply_text(
                msg.RESUME_REQUEST,
                reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
            )
            return WAITING_RESUME
            
        elif text == msg.BUTTON_CONTACT_ADMIN:
            admin_id = ADMIN_ID
            admin_username = os.getenv('ADMIN_USERNAME', 'администратором')
            await update.message.reply_text(
                f"Для связи с администратором, напишите: @rfatyhov",
                reply_markup=get_main_menu_keyboard(is_admin(update.message.from_user.id))
            )
            return MAIN_MENU
            
        elif text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU
            
        else:
            # Обработка полученного резюме
            global feedback_counter
            feedback_counter += 1
            ticket_id = f"R{feedback_counter}"
            
            user = update.message.from_user
            admin_message = f"""Новое резюме {ticket_id}
От: {user.first_name} {user.last_name} (@{user.username})
Резюме:
{text}"""
            
            # Отправка резюме администратору
            admin_id = ADMIN_ID
            if admin_id:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=admin_message)
                except Exception as e:
                    logger.error(f"Failed to send resume to admin: {e}")
            
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(
                "Спасибо за отправку резюме! Мы рассмотрим его и свяжемся с вами.",
                reply_markup=reply_markup
            )
            return MAIN_MENU
            
    except Exception as e:
        logger.error(f"Error in resume handler: {e}")
        await update.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reply to feedback"""
    try:
        query = update.callback_query
        await query.answer()

        # Extract feedback ID from callback data
        feedback_id = query.data.replace('reply_', '')
        
        # Store feedback ID in context for later use
        context.user_data['reply_to_feedback'] = feedback_id
        
        # Ask admin to enter reply text
        await query.message.reply_text(
            "Введите текст ответа:",
            reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
        )
        return WAITING_REPLY

    except Exception as e:
        logger.error(f"Error in admin reply handler: {e}")
        await query.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def handle_admin_reply_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reply text"""
    try:
        if not is_admin(update.message.from_user.id):
            return MAIN_MENU

        reply_text = update.message.text
        feedback_id = context.user_data.get('reply_to_feedback')
        
        if not feedback_id or reply_text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU

        # Get feedback data from global storage
        feedback_data = feedbacks.get(feedback_id)
        if feedback_data and 'user_id' in feedback_data:
            try:
                # Send reply to user
                await context.bot.send_message(
                    chat_id=feedback_data['user_id'],
                    text=f"Ответ на ваше обращение:\n\n{reply_text}"
                )
                await update.message.reply_text("Ответ успешно отправлен!")
            except Exception as e:
                logger.error(f"Error sending reply to user: {e}")
                await update.message.reply_text("Ошибка при отправке ответа пользователю.")
        else:
            await update.message.reply_text("Не удалось найти данные обращения.")

        # Return to main menu
        is_admin_user = is_admin(update.message.from_user.id)
        reply_markup = get_main_menu_keyboard(is_admin_user)
        await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in admin reply text handler: {e}")
        await update.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def start_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start reply to ticket process"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer(msg.ADMIN_NO_RIGHTS, show_alert=True)
        return MAIN_MENU

    ticket_id = query.data.split('_')[1]
    context.user_data['reply_to_ticket'] = ticket_id
    
    await query.message.reply_text(
        msg.ADMIN_REPLY_REQUEST.format(ticket_id=ticket_id),
        reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
    )
    return WAITING_REPLY

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reply to ticket"""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text(msg.ADMIN_NO_RIGHTS)
        return MAIN_MENU

    text = update.message.text

    if text == msg.BUTTON_BACK:
        reply_markup = get_main_menu_keyboard(True)
        await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
        return MAIN_MENU

    ticket_id = context.user_data.get('reply_to_ticket')
    if not ticket_id or ticket_id not in active_tickets:
        await update.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

    user_id = active_tickets[ticket_id]['user_id']

    try:
        # Send reply to user
        await context.bot.send_message(
            chat_id=user_id,
            text=msg.USER_REPLY_RECEIVED.format(
                ticket_id=ticket_id,
                reply=text
            )
        )
        
        reply_markup = get_main_menu_keyboard(True)
        await update.message.reply_text(
            msg.ADMIN_REPLY_SENT.format(ticket_id=ticket_id),
            reply_markup=reply_markup
        )
    except TelegramError as e:
        logger.error(f"Failed to send reply to user {user_id}: {e}")
        reply_markup = get_main_menu_keyboard(True)
        await update.message.reply_text(
            msg.ADMIN_REPLY_FAILED.format(ticket_id=ticket_id),
            reply_markup=reply_markup
        )

    return MAIN_MENU

async def handle_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message and media"""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text(msg.ADMIN_NO_RIGHTS)
        return MAIN_MENU

    message = update.message
    logger.info(f"Processing message in broadcast handler")
    
    # Проверяем кнопку "Назад" до проверки типа сообщения
    if hasattr(message, 'text') and message.text == msg.BUTTON_BACK:
        logger.info("Back button pressed in broadcast")
        reply_markup = get_main_menu_keyboard(is_admin(message.from_user.id))
        await message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
        return MAIN_MENU

    success_count = 0
    fail_count = 0
    broadcast_text = None
    broadcast_media = None
    
    try:
        if message.photo:
            logger.info("Got photo message")
            broadcast_media = message.photo[-1].file_id
            broadcast_text = message.caption
            
            # Отправляем всем пользователям
            for user_id in users_data.keys():
                try:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=broadcast_media,
                        caption=broadcast_text
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send photo to {user_id}: {e}")
                    fail_count += 1
                    
        elif message.video:
            logger.info("Got video message")
            broadcast_media = message.video.file_id
            broadcast_text = message.caption
            
            # Отправляем всем пользователям
            for user_id in users_data.keys():
                try:
                    await context.bot.send_video(
                        chat_id=user_id,
                        video=broadcast_media,
                        caption=broadcast_text
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send video to {user_id}: {e}")
                    fail_count += 1
                    
        elif message.text:
            logger.info("Got text message")
            broadcast_text = message.text
            
            # Отправляем всем пользователям
            for user_id in users_data.keys():
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=broadcast_text
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send text to {user_id}: {e}")
                    fail_count += 1
        
        else:
            logger.warning("Unsupported message type in broadcast")
            await message.reply_text("Этот тип сообщения не поддерживается для рассылки. Пожалуйста, отправьте текст, фото или видео.")
            return WAITING_BROADCAST
            
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await message.reply_text("Произошла ошибка при отправке рассылки. Попробуйте еще раз.")
        return WAITING_BROADCAST

    # Отправляем отчет о результатах
    reply_markup = get_main_menu_keyboard(is_admin(message.from_user.id))
    await message.reply_text(
        msg.ADMIN_BROADCAST_COMPLETE.format(success=success_count, fail=fail_count),
        reply_markup=reply_markup
    )
    return MAIN_MENU

def calculate_location_rating(location):
    """Calculate average rating for a location"""
    total_drink_rating = 0
    total_service_rating = 0
    drink_count = 0
    service_count = 0
    
    for user_data in users_data.values():
        if 'ratings' in user_data:
            for rating in user_data['ratings']:
                if rating['location'] == location:
                    if 'drink_rating' in rating:
                        total_drink_rating += rating['drink_rating']
                        drink_count += 1
                    if 'service_rating' in rating:
                        total_service_rating += rating['service_rating']
                        service_count += 1
    
    avg_drink = round(total_drink_rating / drink_count, 1) if drink_count > 0 else 0
    avg_service = round(total_service_rating / service_count, 1) if service_count > 0 else 0
    total_ratings = max(drink_count, service_count)
    
    return avg_drink, avg_service, total_ratings

def get_location_button_text(location):
    """Get button text with rating for location"""
    avg_drink, avg_service, total = calculate_location_rating(location)
    if total > 0:
        rating_text = f" (⭐️ {avg_drink}/5 • 👤 {total})"
    else:
        rating_text = ""
    return f"{location}{rating_text}"

async def send_location_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send location selection keyboard with ratings"""
    keyboard = [
        [KeyboardButton(get_location_button_text("Дегтярев"))],
        [KeyboardButton(get_location_button_text("Сити Молл"))],
        [KeyboardButton(msg.BUTTON_BACK)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(msg.CHOOSE_LOCATION, reply_markup=reply_markup)
    return LOCATION_SELECTION

def main():
    """Start the bot"""
    try:
        # Load saved users data
        load_users_data()

        # Create application
        application = Application.builder().token(BOT_TOKEN).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                MAIN_MENU: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_FEEDBACK}$"), handle_main_menu),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_MENU}$"), handle_main_menu),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_VACANCIES}$"), handle_main_menu),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_COOPERATION}$"), handle_main_menu),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_SUGGESTIONS}$"), handle_main_menu),
                    MessageHandler(filters.Regex(f"^{msg.ADMIN_BUTTON_BROADCAST}$"), handle_main_menu),
                    MessageHandler(filters.Regex(f"^{msg.ADMIN_BUTTON_USERS}$"), handle_main_menu),
                ],
                LOCATION_SELECTION: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location_selection),
                ],
                RATING_DRINKS: [
                    CommandHandler('start', start),
                    CallbackQueryHandler(handle_drink_rating, pattern='^rate_')
                ],
                RATING_SERVICE: [
                    CommandHandler('start', start),
                    CallbackQueryHandler(handle_service_rating, pattern='^rate_')
                ],
                FEEDBACK: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback),
                ],
                WAITING_RESUME: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                    MessageHandler(filters.Document.ALL | filters.TEXT, handle_resume),
                ],
                COOPERATION_MENU: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cooperation_menu),
                ],
                WAITING_BROADCAST: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                    MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND, handle_broadcast_text),
                ],
                WAITING_REPLY: [
                    CommandHandler('start', start),
                    MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_reply_text),
                ]
            },
            fallbacks=[
                CommandHandler('start', start),
                MessageHandler(filters.Regex(f"^{msg.BUTTON_BACK}$"), handle_main_menu),
                CallbackQueryHandler(handle_admin_reply, pattern='^reply_'),
            ]
        )

        application.add_handler(conv_handler)

        # Start the bot
        application.run_polling()

    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
