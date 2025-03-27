
import logging
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from calendar_utils import add_task
from dateutil.parser import parse as dt_parse
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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

def handle_message(update, context):
    text = update.message.text
    task, duration, date = parse_input(text)
    if not task:
        update.message.reply_text("⚠️ Формат: задача – 1ч – дата (например: дизайн – 2ч – завтра)")
        return

    event = add_task(task, duration, date)
    if event:
        start = event['start']['dateTime'][11:16]
        end = event['end']['dateTime'][11:16]
        date_str = date.strftime('%d.%m')
        update.message.reply_text("✅ Задача добавлена {} с {} до {}".format(date_str, start, end))
    else:
        update.message.reply_text("❌ Нет свободного времени в этот день.")

def start(update, context):
    update.message.reply_text("Привет! Отправь задачу в формате:

задача – 1ч – завтра")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
