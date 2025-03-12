from aiogram import Router, F, types
from aiogram.filters import Command
from database.crud import get_product

router = Router()

@router.message(Command("food"))
async def food_search(message: types.Message):
    await message.answer("🔍 Введите название продукта:")

@router.message(F.text & ~F.command())  # Фильтр исключает ВСЕ команды
async def show_product(message: types.Message):
    product = await get_product(message.text.lower())
    if product:
        response = (
            f"🍏 {product.name.capitalize()} (100 г):\n"
            f"🔥 {product.calories} ккал\n"
            f"🍞 {product.carbs} г углеводов\n"
            f"📉 ГИ: {product.gi}"
        )
    else:
        response = "❌ Продукт не найден"
    await message.answer(response)
    
@router.message(F.text & ~F.command())
async def log_meal(message: types.Message):
    try:
        product_name, quantity = message.text.split()
        quantity = int(quantity)
        
        # Получаем продукт из БД
        product = await get_product(product_name.lower())
        if not product:
            return await message.answer("❌ Продукт не найден")
            
        # Рассчитываем калории
        calories = (product.calories * quantity) // 100
        
        # Сохраняем в историю
        async with async_session() as session:
            session.add(MealRecord(
                user_id=message.from_user.id,
                product_id=product.id,
                quantity=quantity,
                calories=calories
            ))
            await session.commit()
            
        await message.answer(f"✅ {quantity} г {product.name} ({calories} ккал) добавлено!")
        
    except ValueError:
        await message.answer("❌ Формат: <продукт> <граммы>\nПример: `яблоко 150`", parse_mode="Markdown")