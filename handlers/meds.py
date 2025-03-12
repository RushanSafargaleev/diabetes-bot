from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("meds"))
async def meds_list(message: types.Message):
    await message.answer("💊 Список препаратов:\n- Метформин 500 мг")