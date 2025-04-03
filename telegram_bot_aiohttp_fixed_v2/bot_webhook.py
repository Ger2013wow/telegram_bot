import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

from calendar_utils import add_task, get_daily_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

TOKEN = "7555935793:AAH1cJk4dpJhUiyB9IwBKv3-R4rHaLOmAAo"
WEBHOOK_URL = "https://telegrambot-production-dd00.up.railway.app/webhook"

application: Application = ApplicationBuilder().token(TOKEN).build()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        logging.warning("Получено пустое сообщение или не текст.")
        return

    text = update.message.text.strip()
    logging.info(f"📩 Получено сообщение: {text}")

    if text.lower() == "сводка":
        try:
            summary = get_daily_summary()
            logging.info("✅ Сводка успешно получена.")
            await update.message.reply_text(summary)
        except Exception as e:
            logging.exception("Ошибка при получении сводки")
            await update.message.reply_text("⚠️ Ошибка при получении сводки.")
        return

    try:
        parts = [part.strip() for part in text.split(";")]
        logging.info(f"📦 Разобранные части: {parts}")

        if len(parts) != 3:
            raise ValueError("Ожидается ровно 3 параметра, разделённых точкой с запятой.")

        task, duration_str, date = parts
        logging.info(f"📋 Задача: {task}, Длительность: {duration_str}, Дата: {date}")

        duration = int(duration_str)
        logging.info("⏱ Продолжительность успешно преобразована в число.")

        result = add_task(task, duration, date)
        logging.info(f"✅ Задача добавлена: {result}")

        await update.message.reply_text(f"✅ Задача добавлена: {result.get('summary')}")
    except ValueError as ve:
        logging.warning(f"⚠️ Ошибка валидации: {ve}")
        await update.message.reply_text(
            f"⚠️ Ошибка: {ve}\nФормат: задача; продолжительность(мин); дата (YYYY-MM-DD)"
        )
    except Exception as e:
        logging.exception("❌ Необработанная ошибка при добавлении задачи")
        await update.message.reply_text(
            "⚠️ Ошибка при добавлении задачи. Проверьте формат:\n"
            "задача; продолжительность(мин); дата (YYYY-MM-DD)"
        )


application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


async def webhook_handler(request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text="ok")
    except Exception as e:
        logging.exception("❌ Ошибка в webhook_handler")
        return web.Response(status=500, text="Internal Server Error")


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
