import json
import random
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import QUESTIONS_FILE
from keyboards import get_main_keyboard
from utils.tts import generate_voice

# Загрузка вопросов из файла
try:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        QUESTIONS = json.load(f)
except Exception as e:
    logging.error(f"Ошибка загрузки файла вопросов: {e}")
    QUESTIONS = []

# Глобальный словарь для хранения данных пользователей
user_data = {}

def get_user_data(user_id):
    """Возвращает структуру данных для конкретного пользователя, создаёт при отсутствии."""
    if user_id not in user_data:
        user_data[user_id] = {
            "easy_done": [],
            "hard_done": [],
            "last_question": None,
            "language": "en",
            "auto_repeat": False,
            # Счётчики для текущего вопроса
            "answer_display_count": 0,    # для кнопки "Ответ"
            "q_translate_count": 0,       # для кнопки "Перевод вопроса"
            "a_translate_count": 0,       # для кнопки "Перевод ответа"
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Считываем пришедшее сообщение
    # Приводим к нижнему регистру и удаляем пробелы в начале и конце
    msg = update.message.text.strip().lower()
    logging.info(f"[DEBUG] Получено сообщение: '{msg}'")

    data = get_user_data(user_id)
    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")

    # Обновляем язык в структуре пользователя
    data["language"] = lang
    context.user_data["language"] = lang

    # Определяем тексты кнопок (в нижнем регистре)
    btn_next    = "✈️ следующий вопрос" if lang == "ru" else "✈️ next question"
    btn_answer  = "💬 ответ" if lang == "ru" else "💬 answer"
    btn_q_trans = "🌍 перевод вопроса" if lang == "ru" else "🌍 translate question"
    btn_a_trans = "🇷🇺 перевод ответа" if lang == "ru" else "🇷🇺 translate answer"
    btn_support = "💳 поддержать проект" if lang == "ru" else "💳 support project"

    logging.info(f"[DEBUG] Ожидаемые кнопки: {btn_next=}, {btn_answer=}, {btn_q_trans=}, {btn_a_trans=}, {btn_support=}")

    # --- Кнопка "Поддержать проект"
    if btn_support in msg:
        text_support = (
            "💳 Вы можете поддержать проект здесь:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
            if lang == "ru"
            else
            "💳 You can support the project here:\nhttps://www.sberbank.com/sms/pbpn?requisiteNumber=79155691550"
        )
        await update.message.reply_text(text_support)
        return

    # --- Кнопка "Следующий вопрос"
    if btn_next in msg:
        # Получаем список вопросов, на которые пользователь не ответил
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]

        # Если вопросы закончились
        if not available:
            # Если это были простые вопросы, предлагаем перейти к сложным или сбросить
            if level == "easy":
                if lang == "ru":
                    keyboard = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("Перейти к сложным", callback_data="switch_to_hard"),
                            InlineKeyboardButton("Начать сначала", callback_data="reset_progress")
                        ]
                    ])
                    prompt = "✅ Вы ответили на все простые вопросы. Что хотите сделать дальше?"
                else:
                    keyboard = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("Switch to hard", callback_data="switch_to_hard"),
                            InlineKeyboardButton("Start over", callback_data="reset_progress")
                        ]
                    ])
                    prompt = "✅ All easy questions done. Choose next step:"
                await update.message.reply_text(prompt, reply_markup=keyboard)
            else:
                # Если это были сложные вопросы, только сброс
                if lang == "ru":
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Начать сначала", callback_data="reset_progress")]
                    ])
                    prompt = "✅ Все вопросы завершены. Хотите начать сначала?"
                else:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Start over", callback_data="reset_progress")]
                    ])
                    prompt = "✅ All questions completed. Start over?"
                await update.message.reply_text(prompt, reply_markup=keyboard)
            return

        # Выбираем случайный доступный вопрос
        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question

        # Сбрасываем счётчики для нового вопроса
        data["answer_display_count"] = 0
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0

        # Отправляем вопрос (на английском)
        await update.message.reply_text(f"📝 {question['question_en']}")
        voice = generate_voice(question['question_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # --- Кнопка "Ответ"
    if btn_answer in msg:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first."
            )
            return
        count = data["answer_display_count"]
        if count == 0:
            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
        elif count == 1:
            await update.message.reply_text(
                "❗ Ответ уже выведен" if lang == "ru" else "❗ Answer already displayed"
            )
            data["answer_display_count"] = 2
        else:
            # Больше не показываем
            return
        return

    # --- Кнопка "Перевод вопроса"
    if btn_q_trans in msg:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first."
            )
            return
        q_count = data["q_translate_count"]
        if q_count == 0:
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        elif q_count == 1:
            await update.message.reply_text(
                "❗ Вопрос уже переведен" if lang == "ru" else "❗ Question already translated"
            )
            data["q_translate_count"] = 2
        else:
            # Ничего не делаем
            return
        return

    # --- Кнопка "Перевод ответа"
    if btn_a_trans in msg:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang == "ru" else "❗ Please select a question first."
            )
            return
        # Сначала проверяем, что был показан основной ответ
        if data["answer_display_count"] == 0:
            await update.message.reply_text(
                "❗ Сначала получите основной ответ" if lang == "ru" else "❗ Please display the main answer first"
            )
            return
        a_count = data["a_translate_count"]
        if a_count == 0:
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        elif a_count == 1:
            await update.message.reply_text(
                "❗ Ответ уже переведен" if lang == "ru" else "❗ Answer already translated"
            )
            data["a_translate_count"] = 2
        else:
            return
        return

    # Если не совпало ни с одной кнопкой
    await update.message.reply_text(
        "❓ Используй кнопки меню." if lang == "ru" else "❓ Please use the menu buttons."
    )
