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
from handlers.admin import get_admin_handlers, get_admin_block_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("support", support_command))

for handler in get_settings_handlers():
    app.add_handler(handler)

for handler in get_admin_handlers():
    app.add_handler(handler)
for handler in get_admin_block_handlers():
    app.add_handler(handler)

# Универсальный обработчик для всех текстовых сообщений для отладки
async def message_dispatcher(update, context):
    if update.message and update.message.text:
        logging.info(f"[DEBUG] Получено сообщение: '{update.message.text}'")
    else:
        logging.info("[DEBUG] Нет текста в update.message")
    if context.user_data.get("feedback_mode"):
        await handle_feedback_message(update, context)
    else:
        await handle_user_message(update, context)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))

# Добавляем также универсальный обработчик для всех обновлений (если нужно)
# async def all_updates(update, context):
#     logging.info(f"[DEBUG] Update: {update}")
# app.add_handler(MessageHandler(filters.ALL, all_updates))

logging.info("🤖 Бот запущен...")
app.run_polling()
