import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
import asyncio
import threading

from calendar_utils import add_task, get_daily_summary

logging.basicConfig(level=logging.INFO)

TOKEN = "7555935793:AAH1cJk4dpJhUiyB9IwBKv3-R4rHaLOmAAo"
WEBHOOK_URL = "https://telegrambot-production-dd00.up.railway.app/webhook"

flask_app = Flask(__name__)
application: Application = ApplicationBuilder().token(TOKEN).build()

# Обработка входящих сообщений
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

# Webhook endpoint без async
@flask_app.route("/webhook", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# Инициализация и запуск
async def run_bot():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)

def start_bot():
    asyncio.run(run_bot())

if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    flask_app.run(host="0.0.0.0", port=8080)