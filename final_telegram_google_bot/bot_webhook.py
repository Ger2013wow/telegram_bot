import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from calendar_utils import add_task, get_daily_summary

TOKEN = os.getenv("TELEGRAM_TOKEN")

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
            event = add_task(task, duration, date)
            await update.message.reply_text(f"✅ Задача добавлена: {event.get('summary')}")
        except Exception as e:
            await update.message.reply_text("⚠️ Формат: задача; продолжительность(мин); дата (YYYY-MM-DD)")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=os.environ["WEBHOOK_URL"]
    )