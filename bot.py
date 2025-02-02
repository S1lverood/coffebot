import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from telegram.error import TelegramError
import messages as msg

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# States
MAIN_MENU, RATING, FEEDBACK, COOPERATION_MENU, WAITING_BROADCAST, WAITING_REPLY = range(6)

# File paths
USERS_FILE = 'users_data.json'
USERS_LIST_FILE = 'users_list.txt'

# Store user data
users_data = {}
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
    return str(user_id) == os.getenv('ADMIN_ID')

def get_main_menu_keyboard(is_admin_user: bool = False):
    """Get main menu keyboard"""
    keyboard = [
        [msg.BUTTON_QUALITY, msg.BUTTON_SERVICE],
        [msg.BUTTON_COOPERATION, msg.BUTTON_SUGGESTIONS]
    ]
    if is_admin_user:
        keyboard.append([msg.ADMIN_BUTTON_BROADCAST, msg.ADMIN_BUTTON_USERS])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cooperation_keyboard():
    """Get cooperation menu keyboard"""
    keyboard = [
        [msg.BUTTON_BUY_FRANCHISE],
        [msg.BUTTON_OTHER_QUESTION],
        [msg.BUTTON_BACK]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_rating_keyboard():
    """Get rating inline keyboard"""
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f'rate_{i}') for i in range(1, 6)],
        [InlineKeyboardButton(msg.BUTTON_BACK, callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def save_user_data(user):
    """Save user data to storage"""
    if user.id not in users_data:
        users_data[str(user.id)] = {
            'username': user.username or '',
            'first_name': user.first_name or '',
            'last_name': user.last_name or ''
        }
        save_users_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    try:
        user = update.message.from_user
        save_user_data(user)
        is_admin_user = is_admin(user.id)
        reply_markup = get_main_menu_keyboard(is_admin_user)
        await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await update.message.reply_text(msg.ERROR_GENERAL)
        return ConversationHandler.END

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu options"""
    try:
        text = update.message.text

        if text == msg.BUTTON_QUALITY:
            reply_markup = get_rating_keyboard()
            await update.message.reply_text(msg.RATE_QUALITY, reply_markup=reply_markup)
            context.user_data['feedback_type'] = 'quality'
            return RATING

        elif text == msg.BUTTON_SERVICE:
            reply_markup = get_rating_keyboard()
            await update.message.reply_text(msg.RATE_SERVICE, reply_markup=reply_markup)
            context.user_data['feedback_type'] = 'service'
            return RATING

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
            # Save users list to file
            save_users_list()
            
            # Send file to admin
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

async def handle_cooperation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cooperation menu options"""
    try:
        text = update.message.text

        if text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU

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

async def handle_rating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rating callback"""
    try:
        query = update.callback_query
        await query.answer()

        if query.data == 'back_to_main':
            is_admin_user = is_admin(query.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await query.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            await query.message.delete()
            return MAIN_MENU

        rating = int(query.data.split('_')[1])
        feedback_type = context.user_data.get('feedback_type')
        
        if rating == 5:
            is_admin_user = is_admin(query.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await query.message.reply_text(
                msg.THANKS_QUALITY_5 if feedback_type == 'quality' else msg.THANKS_SERVICE_5,
                reply_markup=reply_markup
            )
            await query.message.delete()
            return MAIN_MENU
        else:
            await query.message.reply_text(
                msg.FEEDBACK_QUALITY_REQUEST if feedback_type == 'quality' else msg.FEEDBACK_SERVICE_REQUEST,
                reply_markup=ReplyKeyboardMarkup([[msg.BUTTON_BACK]], resize_keyboard=True)
            )
            await query.message.delete()
            return FEEDBACK

    except Exception as e:
        logger.error(f"Error in rating callback handler: {e}")
        await query.message.reply_text(msg.ERROR_GENERAL)
        return MAIN_MENU

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feedback text"""
    try:
        text = update.message.text

        if text == msg.BUTTON_BACK:
            is_admin_user = is_admin(update.message.from_user.id)
            reply_markup = get_main_menu_keyboard(is_admin_user)
            await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
            return MAIN_MENU

        global feedback_counter
        feedback_counter += 1
        feedback_id = f"#{feedback_counter:04d}"
        
        user = update.message.from_user
        feedback_type = context.user_data.get('feedback_type', 'unknown')
        
        save_user_data(user)

        # Save ticket info
        active_tickets[feedback_id] = {
            'user_id': str(user.id),
            'feedback_type': feedback_type,
            'message': text,
            'timestamp': datetime.now().isoformat()
        }

        # Send message to admin
        admin_id = os.getenv('ADMIN_ID')
        if admin_id:
            keyboard = [[InlineKeyboardButton(msg.ADMIN_BUTTON_REPLY, callback_data=f'reply_{feedback_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            admin_message = msg.ADMIN_NEW_TICKET.format(
                ticket_id=feedback_id,
                feedback_type=feedback_type,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                message=text
            )
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    reply_markup=reply_markup
                )
            except TelegramError as e:
                logger.error(f"Failed to send message to admin: {e}")

        is_admin_user = is_admin(user.id)
        reply_markup = get_main_menu_keyboard(is_admin_user)
        await update.message.reply_text(msg.FEEDBACK_THANKS, reply_markup=reply_markup)
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Error in feedback handler: {e}")
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
    """Handle broadcast message text"""
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text(msg.ADMIN_NO_RIGHTS)
        return MAIN_MENU

    text = update.message.text

    if text == msg.BUTTON_BACK:
        reply_markup = get_main_menu_keyboard(True)
        await update.message.reply_text(msg.WELCOME_MESSAGE, reply_markup=reply_markup)
        return MAIN_MENU

    success_count = 0
    fail_count = 0

    for user_id in users_data.keys():
        try:
            await context.bot.send_message(chat_id=user_id, text=text)
            success_count += 1
        except TelegramError as e:
            fail_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")

    reply_markup = get_main_menu_keyboard(True)
    await update.message.reply_text(
        msg.ADMIN_BROADCAST_COMPLETE.format(success=success_count, fail=fail_count),
        reply_markup=reply_markup
    )
    return MAIN_MENU

def main():
    """Start the bot"""
    try:
        # Load saved users data
        load_users_data()

        # Create application
        application = Application.builder().token(os.getenv('BOT_TOKEN')).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(msg.CMD_START, start)],
            states={
                MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
                ],
                COOPERATION_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cooperation_menu)
                ],
                RATING: [
                    CallbackQueryHandler(handle_rating_callback)
                ],
                FEEDBACK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)
                ],
                WAITING_BROADCAST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_text)
                ],
                WAITING_REPLY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply)
                ],
            },
            fallbacks=[CommandHandler(msg.CMD_START, start)]
        )

        # Add handlers
        application.add_handler(conv_handler)
        application.add_handler(CallbackQueryHandler(start_reply, pattern=r'^reply_'))

        # Start the bot
        application.run_polling()

    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
