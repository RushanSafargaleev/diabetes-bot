from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from database.crud import create_user, get_user
from database.models import User
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime
from .commands import main_menu

router = Router()

temp_data = {}

def get_registration_keyboard(step: int):
    builder = ReplyKeyboardBuilder()
    if step > 1:
        builder.button(text="◀️ Назад")
    builder.button(text="🚫 Отменить регистрацию")
    return builder.as_markup(resize_keyboard=True)

async def send_current_step(user_id: int, message: Message):
    step = temp_data[user_id]["step"]
    texts = {
        1: "Шаг 1/5: Введите ваше настоящее имя:",
        2: "Шаг 2/5: Введите ваш возраст:",
        3: "Шаг 3/5: Выберите тип диабета:\n1 - 1 тип\n2 - 2 тип\n3 - Гестационный\n4 - Другое",
        4: "Шаг 4/5: Введите ваш вес в кг (пример: 68.5):",
        5: "Шаг 5/5: Введите ваш рост в см (пример: 175):"
    }
    await message.answer(texts[step], reply_markup=get_registration_keyboard(step))

@router.message(Command("register"))
async def start_registration(message: Message):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer("ℹ️ Вы уже зарегистрированы!", reply_markup=main_menu())
        return
    
    temp_data[message.from_user.id] = {"step": 1}
    await send_current_step(message.from_user.id, message)

@router.message(F.text == "🚫 Отменить регистрацию")
async def cancel_registration(message: Message):
    user_id = message.from_user.id
    if user_id in temp_data:
        del temp_data[user_id]
    await message.answer("❌ Регистрация отменена", reply_markup=ReplyKeyboardRemove())

@router.message(F.text == "◀️ Назад")
async def back_step(message: Message):
    user_id = message.from_user.id
    if user_id not in temp_data:
        return
    
    temp_data[user_id]["step"] = max(1, temp_data[user_id]["step"] - 1)
    await send_current_step(user_id, message)

@router.message(F.text & F.from_user.id.in_(temp_data.keys()))
async def process_registration(message: Message):
    user_id = message.from_user.id
    step = temp_data[user_id]["step"]
    
    try:
        if step == 1:
            if len(message.text) < 2:
                raise ValueError("Слишком короткое имя")
            temp_data[user_id]["name"] = message.text
            temp_data[user_id]["step"] = 2
            
        elif step == 2:
            age = int(message.text)
            if not 1 <= age <= 120:
                raise ValueError
            temp_data[user_id]["age"] = age
            temp_data[user_id]["step"] = 3
            
        elif step == 3:
            if message.text not in {"1", "2", "3", "4"}:
                raise ValueError
            temp_data[user_id]["diabetes_type"] = int(message.text)
            temp_data[user_id]["step"] = 4
            
        elif step == 4:
            weight = float(message.text.replace(',', '.'))
            if not 10 <= weight <= 300:
                raise ValueError
            temp_data[user_id]["weight"] = weight
            temp_data[user_id]["step"] = 5
            
        elif step == 5:
            height = float(message.text.replace(',', '.'))
            if not 50 <= height <= 250:
                raise ValueError
            temp_data[user_id]["height"] = height
            
            user = User(
                telegram_id=user_id,
                **{k: v for k, v in temp_data[user_id].items() if k != "step"}
            )
            await create_user(user)
            del temp_data[user_id]
            
            await message.answer(
                "✅ Регистрация успешно завершена!",
                reply_markup=main_menu()
            )
            return
            
        await send_current_step(user_id, message)
        
    except Exception as e:
        error_messages = {
            1: "❌ Некорректное имя! Минимум 2 символа",
            2: "❌ Некорректный возраст! Введите число от 1 до 120",
            3: "❌ Выберите вариант из списка (1-4)",
            4: "❌ Некорректный вес! Пример: 68.5",
            5: "❌ Некорректный рост! Пример: 175"
        }
        await message.answer(error_messages[step])