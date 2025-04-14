    # --- Обработка кнопки "Ответ" ---
    if msg == btn_answer:
        q = data.get("last_question")

        if not q:
            await update.message.reply_text(
                "❗ Сначала выберите вопрос." if lang == "ru"
                else "❗ Please select a question first."
            )
            return

        answer_count = data.get("answer_display_count", 0)

        if answer_count == 0:
            await update.message.reply_text(f"✅ {q['answer_en']}")
            voice = generate_voice(q['answer_en'])
            if voice:
                await update.message.reply_voice(voice)
            data["answer_display_count"] = 1
        else:
            await update.message.reply_text(
                "❗ Ответ уже получен." if lang == "ru"
                else "❗ Answer already shown."
            )
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
            await update.message.reply_text(f"🌍 {q['question_ru']}")
            data["q_translate_count"] = 1
        else:
            await update.message.reply_text(
                "❗ Вопрос уже переведён." if lang == "ru"
                else "❗ Question already translated."
            )
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

        if data.get("answer_display_count", 0) == 0:
            await update.message.reply_text(
                "❗ Сначала получите основной ответ." if lang == "ru"
                else "❗ Please display the main answer first."
            )
            return

        a_trans_count = data.get("a_translate_count", 0)

        if a_trans_count == 0:
            await update.message.reply_text(f"🇷🇺 {q['answer_ru']}")
            data["a_translate_count"] = 1
        else:
            await update.message.reply_text(
                "❗ Ответ уже переведён." if lang == "ru"
                else "❗ Answer already translated."
            )
        return
