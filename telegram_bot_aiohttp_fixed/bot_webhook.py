import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from calendar_utils import add_task, get_daily_summary

logging.basicConfig(level=logging.INFO)

TOKEN = "7555935793:AAH1cJk4dpJhUiyB9IwBKv3-R4rHaLOmAAo"
WEBHOOK_URL = "https://telegrambot-production-dd00.up.railway.app/webhook"

application: Application = ApplicationBuilder().token(TOKEN).build()

# Обработка сообщений
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
        except Exception:
            await update.message.reply_text("⚠️ Формат: задача; продолжительность(мин); дата (YYYY-MM-DD)")

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# aiohttp webhook handler
async def webhook_handler(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="ok")

# Запуск aiohttp app
async def main():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)

    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    logging.info("✅ AIOHTTP server started on port 8080")
    await application.start()
    await application.wait_until_closed()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())