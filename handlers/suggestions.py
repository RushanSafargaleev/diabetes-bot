from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("suggest"))
async def handle_suggestion(message: types.Message):
    await message.answer("💡 Ваше предложение отправлено!")