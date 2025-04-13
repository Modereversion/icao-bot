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
    if user_id not in user_data:
        user_data[user_id] = {
            "easy_done": [],
            "hard_done": [],
            "last_question": None,
            "language": "en",
            "auto_repeat": False,
            # Счётчики для текущего вопроса:
            "answer_display_count": 0,   # для кнопки "Ответ"
            "q_translate_count": 0,      # для кнопки "Перевод вопроса"
            "a_translate_count": 0,      # для кнопки "Перевод ответа"
        }
    return user_data[user_id]

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()
    data = get_user_data(user_id)

    # Получаем язык из контекста (тексты вопросов/ответов всегда на английском)
    lang = context.user_data.get("language", data.get("language", "en"))
    level = context.user_data.get("level", "easy")
    data["language"] = lang
    context.user_data["language"] = lang

    # Генерация меток для кнопок (текст кнопок зависит от языка интерфейса)
    btn_next    = "✈️ Следующий вопрос" if lang == "ru" else "✈️ Next question"
    btn_answer  = "💬 Ответ" if lang == "ru" else "💬 Answer"
    btn_q_trans = "🌍 Перевод вопроса" if lang == "ru" else "🌍 Translate question"
    btn_a_trans = "🇷🇺 Перевод ответа" if lang == "ru" else "🇷🇺 Translate answer"

    logging.info(f"[USER {user_id}] Сообщение: {msg} | Язык: {lang} | Уровень: {level}")

    # --- Обработка кнопки "Следующий вопрос" ---
    if msg == btn_next:
        available = [q for q in QUESTIONS if q["level"] == level and q["id"] not in data[f"{level}_done"]]
        if not available:
            # Если вопросов не осталось для данного уровня:
            if level == "easy":
                # Для простых вопросов – предлагаем два варианта: начать сложные или начать сначала (сброс статистики)
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Перейти к сложным", callback_data="switch_to_hard"),
                        InlineKeyboardButton("Начать сначала", callback_data="reset_progress")
                    ]
                ])
                await update.message.reply_text(
                    "✅ Вы ответили на все простые вопросы. Что хотите сделать дальше?" if lang == "ru"
                    else "✅ All easy questions done. Choose next step:",
                    reply_markup=keyboard
                )
            else:
                # Для сложных вопросов – предлагаем только вариант начать сначала
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Начать сначала", callback_data="reset_progress")]
                ])
                await update.message.reply_text(
                    "✅ Все вопросы завершены. Хотите начать сначала?" if lang == "ru"
                    else "✅ All questions completed. Start over?",
                    reply_markup=keyboard
                )
            return

        question = random.choice(available)
        data[f"{level}_done"].append(question["id"])
        data["last_question"] = question

        # Сбрасываем все счётчики для нового вопроса
        data["answer_display_count"] = 0
        data["q_translate_count"] = 0
        data["a_translate_count"] = 0

        # Отправляем вопрос на английском независимо от выбранного языка интерфейса
        await update.message.reply_text(f"📝 {question['question_en']}")
        voice = generate_voice(question['question_en'])
        if voice:
            await update.message.reply_voice(voice)
        return

    # --- Обработка кнопки "Ответ" ---
    if msg == btn_answer:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang 
                == "ru" else "❗ Please select a question first."
            )
            return
        answer_count = data.get("answer_display_count", 0)
        if answer_count == 0:
            # Первый раз отправляем основной ответ (на английском)
            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
        elif answer_count == 1:
            # Второй раз – сообщаем, что ответ уже выведен
            await update.message.reply_text(
                "❗ Ответ уже выведен" if lang == "ru" else "❗ Answer already displayed"
            )
            data["answer_display_count"] = 2
        else:
            # Третье и последующие нажатия – никаких действий
            return
        return

    # --- Обработка кнопки "Перевод вопроса" ---
    if msg == btn_q_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang == "ru" 
                else "❗ Please select a question first."
            )
            return
        q_trans_count = data.get("q_translate_count", 0)
        if q_trans_count == 0:
            # Первый раз отправляем перевод вопроса (на русском)
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        elif q_trans_count == 1:
            # Второй раз – сообщение, что перевод уже выполнен
            await update.message.reply_text(
                "❗ Вопрос уже переведен" if lang == "ru" else "❗ Question already translated"
            )
            data["q_translate_count"] = 2
        else:
            # Третье и последующие нажатия – ничего не делаем
            return
        return

    # --- Обработка кнопки "Перевод ответа" ---
    if msg == btn_a_trans:
        q = data.get("last_question")
        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang == "ru" 
                else "❗ Please select a question first."
            )
            return
        # Если основной ответ ещё не был выведен, не выполняем перевод
        if data.get("answer_display_count", 0) == 0:
            await update.message.reply_text(
                "❗ Сначала получите основной ответ" if lang == "ru" 
                else "❗ Please display the main answer first"
            )
            return
        a_trans_count = data.get("a_translate_count", 0)
        if a_trans_count == 0:
            # Первый раз отправляем перевод ответа (на русском)
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        elif a_trans_count == 1:
            # Второй раз – сообщение, что перевод уже выполнен
            await update.message.reply_text(
                "❗ Ответ уже переведен" if lang == "ru" else "❗ Answer already translated"
            )
            data["a_translate_count"] = 2
        else:
            # Третье и последующие нажатия – никаких действий
            return
        return

    await update.message.reply_text(
        "❓ Используй кнопки меню." if lang == "ru" 
        else "❓ Please use the menu buttons."
    )
