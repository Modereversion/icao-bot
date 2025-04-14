import json
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN
from handlers.commands import start_command, support_command
from handlers.questions import handle_user_message
from handlers.settings import get_settings_handlers
from handlers.admin import get_admin_handlers
from handlers.feedback import handle_feedback_message

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Создаём приложение
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Загружаем список вопросов в память (используется в handlers.questions)
with open("questions.json", encoding="utf-8") as f:
    app.bot_data["questions"] = json.load(f)

# Обработка команды /start
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("support", support_command))

# Обработчики меню (настройки)
for handler in get_settings_handlers():
    app.add_handler(handler)

# Обработчики админ-панели
for handler in get_admin_handlers():
    app.add_handler(handler)

# Обработка обычных текстовых сообщений (вопросы, переводы, ответы, отзывы)
async def message_dispatcher(update, context):
    if context.user_data.get("feedback_mode"):
        await handle_feedback_message(update, context)
    else:
        await handle_user_message(update, context)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))

# Запуск бота
if __name__ == "__main__":
    logging.info("🚀 Бот запущен!")
    app.run_polling()
