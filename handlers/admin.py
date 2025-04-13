from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from config import ADMIN_ID
from handlers.questions import user_data  # Глобальный словарь пользователей
from handlers.feedback import feedback_list

# Множество заблокированных пользователей
BLOCKED_USERS = set()

async def management_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("language", "en")
    # Проверяем, что вызывающий пользователь – администратор
    if user_id != ADMIN_ID:
        return
    # Формируем inline-клавиатуру с опциями административного меню
    if lang == "ru":
        buttons = [
            [InlineKeyboardButton("Просмотреть статистику", callback_data="admin_view_stats")],
            [InlineKeyboardButton("Полная статистика", callback_data="admin_full_stats")],
            [InlineKeyboardButton("Отзывы", callback_data="admin_view_feedbacks")],
            [InlineKeyboardButton("Очистить отзывы", callback_data="admin_clear_feedbacks")],
            [InlineKeyboardButton("Заблокировать пользователя", callback_data="admin_block_user")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("View stats", callback_data="admin_view_stats")],
            [InlineKeyboardButton("Full stats", callback_data="admin_full_stats")],
            [InlineKeyboardButton("Feedbacks", callback_data="admin_view_feedbacks")],
            [InlineKeyboardButton("Clear feedbacks", callback_data="admin_clear_feedbacks")],
            [InlineKeyboardButton("Block user", callback_data="admin_block_user")]
        ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🛠️ Админ-панель:" if lang == "ru" else "🛠️ Admin panel:", reply_markup=keyboard)

async def admin_management_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("language", "en")
    
    if query.data == "admin_view_stats":
        total_users = len(user_data)
        text = f"📈 Всего пользователей: {total_users}" if lang == "ru" else f"📈 Total users: {total_users}"
        await query.edit_message_text(text)
    elif query.data == "admin_full_stats":
        # Формируем подробную статистику для каждого пользователя
        # Для каждого пользователя выводим: id, first_name, last_name, username, country (в нашем случае language_code),
        # дату первого запуска (если такая информация сохранялась)
        if not user_data:
            text = "Нет данных по пользователям" if lang == "ru" else "No user data available"
        else:
            lines = []
            for uid, data in user_data.items():
                # Если таких ключей нет, выводим "-"
                first_name = data.get("first_name", "-")
                last_name = data.get("last_name", "-")
                username = data.get("username", "-")
                country = data.get("country", "-")
                first_launch = data.get("first_launch", "-")
                line = f"ID: {uid} | {first_name} {last_name} (@{username}) | {country} | {first_launch}"
                lines.append(line)
            text = "\n".join(lines)
        await query.edit_message_text(text if text else "Нет данных" if lang == "ru" else "No data")
    elif query.data == "admin_view_feedbacks":
        if not feedback_list:
            text = "Нет отзывов" if lang == "ru" else "No feedbacks"
        else:
            text = "\n\n".join(feedback_list)
        await query.edit_message_text(text)
    elif query.data == "admin_clear_feedbacks":
        feedback_list.clear()
        text = "Отзывы очищены" if lang == "ru" else "Feedbacks cleared"
        await query.edit_message_text(text)
    elif query.data == "admin_block_user":
        # Переводим админа в режим блокировки
        context.user_data["block_mode"] = True
        prompt = "Введите ID пользователя для блокировки:" if lang == "ru" else "Enter user ID to block:"
        await query.edit_message_text(prompt)

def get_admin_handlers():
    return [
        # Обработчик для текстовой команды "Управление" / "Management"
        MessageHandler(filters.Regex("^(Управление|Management)$"), management_menu_command),
        # Обработчик inline callback от административного меню
        CallbackQueryHandler(admin_management_callback, pattern="^admin_.*")
    ]

# Обработчик для блокировки пользователя (при входе в режиме block_mode)
async def admin_block_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что мы в режиме блокировки и что это сообщение от администратора
    user_id = update.effective_user.id
    if user_id != ADMIN_ID or not context.user_data.get("block_mode"):
        return
    text = update.message.text.strip()
    try:
        block_id = int(text)
        BLOCKED_USERS.add(block_id)
        context.user_data["block_mode"] = False
        await update.message.reply_text(f"Пользователь с ID {block_id} заблокирован" if context.user_data.get("language", "en")=="ru" else f"User with ID {block_id} blocked")
    except ValueError:
        await update.message.reply_text("Некорректный ID. Попробуйте снова:" if context.user_data.get("language", "en")=="ru" else "Invalid ID. Please try again:")

def get_admin_block_handlers():
    # Регистрируем отдельный обработчик для ввода ID при блокировке
    return [
        MessageHandler(filters.TEXT, admin_block_user_input)
    ]
