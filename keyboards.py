from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_label(key, lang):
    labels = {
        "next": {"ru": "✈️ Следующий вопрос", "en": "✈️ Next question"},
        "answer": {"ru": "💬 Ответ", "en": "💬 Answer"},
        "q_translate": {"ru": "🌍 Перевод вопроса", "en": "🌍 Translate question"},
        "a_translate": {"ru": "🇷🇺 Перевод ответа", "en": "🇷🇺 Translate answer"},
        "support": {"ru": "💳 Поддержать проект", "en": "💳 Support project"},
        "settings": {"ru": "⚙️ Настройки", "en": "⚙️ Settings"},
    }
    return labels[key][lang]

def get_main_keyboard(user_id, lang="en"):
    return ReplyKeyboardMarkup([
        [get_label("next", lang), get_label("answer", lang)],
        [get_label("q_translate", lang), get_label("a_translate", lang)],
        [get_label("settings", lang), get_label("support", lang)]
    ], resize_keyboard=True)

def get_main_keyboard_no_translation(user_id, lang="en"):
    return ReplyKeyboardMarkup([
        [get_label("next", lang), get_label("answer", lang)],
        [get_label("settings", lang), get_label("support", lang)]
    ], resize_keyboard=True)

def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])

def get_difficulty_keyboard(lang="en", current=None):
    emoji_easy = "🛫"
    emoji_hard = "🚀"
    text_easy = f"{emoji_easy} Лёгкий" if lang == "ru" else f"{emoji_easy} Easy"
    text_hard = f"{emoji_hard} Сложный" if lang == "ru" else f"{emoji_hard} Hard"
    if current == "easy":
        text_easy += " ✅"
    if current == "hard":
        text_hard += " ✅"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text_easy, callback_data="level_easy"),
         InlineKeyboardButton(text_hard, callback_data="level_hard")]
    ])
