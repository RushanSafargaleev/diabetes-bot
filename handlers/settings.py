from aiogram import Router, F, types
from aiogram.filters import Command
from database.crud import update_user_setting

router = Router()

@router.message(Command("set_water"))
async def set_water(message: types.Message):
    try:
        amount = int(message.text.split()[1])
        await update_user_setting(message.from_user.id, "water", amount)
        await message.answer(f"✅ Норма воды установлена: {amount} мл/день")
    except:
        await message.answer("❌ Ошибка. Используйте: /set_water <мл>")

@router.message(Command("set_calories"))
async def set_calories(message: types.Message):
    try:
        amount = int(message.text.split()[1])
        await update_user_setting(message.from_user.id, "calories", amount)
        await message.answer(f"✅ Норма калорий установлена: {amount} ккал/день")
    except:
        await message.answer("❌ Ошибка. Используйте: /set_calories <ккал>")