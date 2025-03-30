import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from calendar_utils import add_task, get_daily_summary

TOKEN = "7555935793:AAH1cJk4dpJhUiyB9IwBKv3-R4rHaLOmAAo"

logging.basicConfig(level=logging.INFO)

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

if __name__ == "__main__":
    from os import environ
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(environ.get("PORT", 8080)),
        webhook_url="https://telegrambot-production-dd00.up.railway.app/webhook"
    )