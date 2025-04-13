import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import BOT_TOKEN
from handlers.commands import start_command, support_command
from handlers.feedback import handle_feedback_message
from handlers.questions import handle_user_message
from handlers.settings import get_settings_handlers
from handlers.admin import get_admin_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Регистрируем обработчики команд
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("support", support_command))

# Регистрируем обработчики настроек
for handler in get_settings_handlers():
    app.add_handler(handler)

# Регистрируем административные обработчики
for handler in get_admin_handlers():
    app.add_handler(handler)

# Регистрируем обработчик текстовых сообщений, который перенаправляет в соответствующие функции
# (включая обработку отзыва и вопросы)
async def message_dispatcher(update, context):
    # Если установлен режим отзыва, перенаправляем сообщение в обработчик отзывов
    if context.user_data.get("feedback_mode"):
        await handle_feedback_message(update, context)
    else:
        await handle_user_message(update, context)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))

logging.info("🤖 Бот запущен...")
app.run_polling()
