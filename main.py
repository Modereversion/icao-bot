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

# Регистрация обработчиков команд
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("support", support_command))

# Регистрация обработчиков настроек
for handler in get_settings_handlers():
    app.add_handler(handler)

# Регистрация административных обработчиков
for handler in get_admin_handlers():
    app.add_handler(handler)

# Создаем пользовательский фильтр для отзывов, используя filters.create
feedback_custom_filter = filters.create(
    lambda update, context: context.user_data.get("feedback_mode", False),
    name="FeedbackFilter"
)
feedback_filter = filters.TEXT & feedback_custom_filter

# Регистрируем обработчик для сообщений-отзывов (срабатывает только, когда feedback_mode True)
app.add_handler(MessageHandler(feedback_filter, handle_feedback_message))
# Регистрируем обработчик для обычных текстовых сообщений (без команд)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

logging.info("🤖 Бот запущен...")
app.run_polling()
