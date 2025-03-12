from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

scheduler = AsyncIOScheduler()

async def send_reminder(bot: Bot, chat_id: int):
    try:
        await bot.send_message(chat_id, "💧 Не забудьте пить воду!")
    except Exception as e:
        print(f"Ошибка: {e}")

async def start_reminders(bot: Bot, chat_id: int):
    scheduler.add_job(
        send_reminder,
        'interval',
        hours=2,
        args=(bot, chat_id)
    )
    scheduler.start()