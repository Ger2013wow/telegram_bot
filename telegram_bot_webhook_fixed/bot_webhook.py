import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from calendar_utils import add_task, get_daily_summary

logging.basicConfig(level=logging.INFO)

TOKEN = "7555935793:AAH1cJk4dpJhUiyB9IwBKv3-R4rHaLOmAAo"
WEBHOOK_PATH = "/webhook"

flask_app = Flask(__name__)
application: Application = ApplicationBuilder().token(TOKEN).build()

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.lower() == "сводка":
        summary = get_daily_summary()
        await update.message.reply_text(summary)
    else:
        try:
            task, duration, date = text.split(";")
            task = task.strip()
            duration = int(duration.strip())
            date = date.strip()
            result = add_task(task, duration, date)
            await update.message.reply_text(f"✅ Задача добавлена: {result.get('summary')}")
        except Exception as e:
            await update.message.reply_text("⚠️ Формат: задача; продолжительность(мин); дата (YYYY-MM-DD)")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@flask_app.post(WEBHOOK_PATH)
async def webhook_handler():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

if __name__ == "__main__":
    import asyncio
    import threading

    # Запуск Telegram-бота в фоне
    def run_bot():
        asyncio.run(application.initialize())
        application.bot.set_webhook(url="https://telegrambot-production-dd00.up.railway.app/webhook")
        application.run_async()

    threading.Thread(target=run_bot).start()

    # Запуск Flask-сервера
    flask_app.run(host="0.0.0.0", port=8080)