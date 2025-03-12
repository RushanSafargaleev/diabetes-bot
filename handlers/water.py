from aiogram import Router, types, F
from aiogram.filters import Command
from database.models import async_session, WaterRecord
from datetime import datetime

router = Router()

@router.message(Command("water"))
async def water_command(message: types.Message):
    await message.answer("💧 Введите выпитый объем в мл:")

@router.message(F.text.isdigit())
async def log_water(message: types.Message):
    amount = int(message.text)
    async with async_session() as session:
        session.add(WaterRecord(
            user_id=message.from_user.id,
            amount=amount,
            date=datetime.now()
        ))
        await session.commit()
    await message.answer(f"✅ Записано {amount} мл!")

@router.message(Command("water_stats"))
async def water_stats(message: types.Message):
    async with async_session() as session:
        result = await session.execute(
            select(WaterRecord.amount)
            .where(WaterRecord.user_id == message.from_user.id)
        )
        total = sum(record.amount for record in result.scalars())
    await message.answer(f"💦 Всего выпито сегодня: {total} мл")