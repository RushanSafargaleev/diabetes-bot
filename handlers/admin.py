from aiogram import Router, types, F
from aiogram.filters import Command
from database.models import async_session, Product

router = Router()

@router.message(Command("add_product"))
async def add_product(message: types.Message):
    # Формат: /add_product Название;Калории;Углеводы;ГИ
    try:
        _, name, calories, carbs, gi = message.text.split(';')
        async with async_session() as session:
            session.add(Product(
                name=name.strip().lower(),
                calories=int(calories),
                carbs=int(carbs),
                gi=int(gi)
            ))
            await session.commit()
        await message.answer("✅ Продукт добавлен!")
    except:
        await message.answer("❌ Ошибка формата. Используйте:\n/add_product Название;Калории;Углеводы;ГИ")