from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import logging

from handlers.commands import router as commands_router
from handlers.registration import router as registration_router
from handlers.profile import router as profile_router
from handlers.side_menu import router as side_menu_router  # Добавленный импорт
from handlers.glucose import router as glucose_router  # Добавить в импорты

from database.models import async_session
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Подключаем все роутеры
dp.include_router(commands_router)
dp.include_router(registration_router)
dp.include_router(profile_router)
dp.include_router(side_menu_router)  # Добавленное подключение
dp.include_router(glucose_router)  # Добавить эту строку

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🩸 Добро пожаловать в Diabetes Assistant Bot!\n\n"
        "Основные команды:\n"
        "/register - регистрация\n"
        "/profile - просмотр профиля\n\n"
        "Бот поможет вам контролировать диабет!"
    )

@dp.update.outer_middleware()
async def session_middleware(handler, event, data):
    async with async_session() as session:
        data["session"] = session
        return await handler(event, data)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        from database.models import create_db
        asyncio.run(create_db())
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    
    asyncio.run(main())