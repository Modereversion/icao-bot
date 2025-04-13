from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters
from config import ADMIN_ID
from handlers.questions import user_data  # предполагается, что это глобальный словарь для статистики

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("language", "en")
    # Проверяем, что сообщение получено от администратора
    if user_id != ADMIN_ID:
        return
    text = "🛠️ Админ-панель:" if lang == "ru" else "🛠️ Admin panel:"
    text += "\n📊 /stats — Статистика"
    # Можно добавить и другие пункты меню админа
    await update.message.reply_text(text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    total_users = len(user_data)
    active_users = sum(1 for u in user_data.values() if u["easy_done"] or u["hard_done"])
    lang = context.user_data.get("language", "en")
    if lang == "ru":
        text = f"📈 Всего пользователей: {total_users}\n🟢 Активных пользователей: {active_users}"
    else:
        text = f"📈 Total users: {total_users}\n🟢 Active users: {active_users}"
    await update.message.reply_text(text)

def get_admin_handlers():
    # Обработчик на сообщение "Управление" (на русском или английском), видимый только администратору
    return [
        MessageHandler(filters.Regex("^(Управление|Management)$"), admin_command),
        CommandHandler("stats", stats_command)
    ]
