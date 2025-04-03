import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from calendar_utils import add_task, get_daily_summary

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

TOKEN = "7555935793:AAH1cJk4dpJhUiyB9IwBKv3-R4rHaLOmAAo"
WEBHOOK_URL = "https://telegrambot-production-dd00.up.railway.app/webhook"

# Создание Telegram-приложения
application: Application = ApplicationBuilder().token(TOKEN).build()


# Обработчик входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        logging.warning("❗ Получено обновление без текста.")
        return

    text = update.message.text.strip()
    logging.info(f"📩 Получено сообщение: {text}")

    if text.lower() == "сводка":
        try:
            summary = get_daily_summary()
            await update.message.reply_text(summary)
        except Exception as e:
            logging.exception("❌ Ошибка при получении сводки")
            await update.message.reply_text("⚠️ Ошибка при получении сводки.")
        return

    # Обработка задачи
    try:
        parts = [part.strip() for part in text.split(";")]
        if len(parts) != 3:
            raise ValueError("Неверное количество параметров.")
        task, duration_str, date = parts

        duration = int(duration_str)
        result = add_task(task, duration, date)

        await update.message.reply_text(f"✅ Задача добавлена: {result.get('summary')}")
    except ValueError as ve:
        await update.message.reply_text(
            f"⚠️ Ошибка: {ve}\nФормат: задача; продолжительность(мин); дата (YYYY-MM-DD)"
        )
    except Exception as e:
        logging.exception("❌ Ошибка при добавлении задачи")
        await update.message.reply_text(
            "⚠️ Непредвиденная ошибка. Проверьте формат:\n"
            "задача; продолжительность(мин); дата (YYYY-MM-DD)"
        )


# Регистрируем обработчик сообщений
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# aiohttp webhook handler
async def webhook_handler(request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text="ok")
    except Exception as e:
        logging.exception("❌ Ошибка в webhook_handler")
        return web.Response(status=500, text="Internal Server Error")


# Запуск aiohttp-приложения
async def main():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"🚀 Webhook установлен: {WEBHOOK_URL}")

    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    logging.info("✅ AIOHTTP сервер запущен на порту 8080")

    await application.start()
    await application.wait_until_closed()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
