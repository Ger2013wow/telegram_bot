import logging
import datetime
import os
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from calendar_utils import add_task
from dateutil.parser import parse as dt_parse

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

def parse_input(text):
    try:
        parts = text.split("–")
        if len(parts) != 3:
            return None, None, None
        task = parts[0].strip()
        duration = float(parts[1].strip().replace('ч', '').replace('h', ''))
        day_str = parts[2].strip().lower()

        today = datetime.date.today()
        if "завтра" in day_str:
            date = today + datetime.timedelta(days=1)
        elif "сегодня" in day_str:
            date = today
        else:
            try:
                date = dt_parse(day_str, dayfirst=True).date()
            except:
                return None, None, None

        return task, duration, date
    except:
        return None, None, None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    task, duration, date = parse_input(text)
    if not task:
        await update.message.reply_text("⚠️ Формат: задача – 1ч – дата (например: дизайн – 2ч – завтра)")
        return

    event = add_task(task, duration, date)
    if event:
        start = event['start']['dateTime'][11:16]
        end = event['end']['dateTime'][11:16]
        date_str = date.strftime('%d.%m')
        await update.message.reply_text(f"✅ Задача добавлена {date_str} с {start} до {end}")
    else:
        await update.message.reply_text("❌ Нет свободного времени в этот день.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь задачу в формате:\n\nзадача – 1ч – завтра")

async def delete_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)

async def main():
    await delete_webhook()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
