from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from database.crud import get_user, update_user
from database.models import User
from datetime import datetime

router = Router()

# Временное хранилище для редактирования профиля
edit_temp = {}

def get_profile_text(user: User) -> str:
    return (
        "📌 **Ваш профиль**\n\n"
        f"👤 Имя: {user.name}\n"
        f"🎂 Возраст: {user.age}\n"
        f"🩺 Тип диабета: {user.diabetes_type}\n"
        f"⚖️ Вес: {user.weight} кг\n"
        f"📏 Рост: {user.height} см\n"
        f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}"
    )

def get_edit_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Имя", callback_data="edit_name")
    builder.button(text="✏️ Возраст", callback_data="edit_age")
    builder.button(text="✏️ Тип диабета", callback_data="edit_diabetes")
    builder.button(text="✏️ Вес", callback_data="edit_weight")
    builder.button(text="✏️ Рост", callback_data="edit_height")
    builder.button(text="🔙 В меню", callback_data="menu")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить редактирование")
    return builder.as_markup(resize_keyboard=True)

@router.message(Command("profile"))
async def show_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала зарегистрируйтесь с помощью /register")
        return
    
    await message.answer(
        get_profile_text(user),
        reply_markup=get_edit_keyboard()
    )

@router.callback_query(F.data.startswith("edit_"))
async def start_edit(callback: CallbackQuery):
    field = callback.data.split("_")[1]
    edit_temp[callback.from_user.id] = {"field": field}
    
    prompts = {
        "name": "Введите новое имя:",
        "age": "Введите новый возраст:",
        "diabetes": "Выберите тип диабета:\n1 - 1 тип\n2 - 2 тип\n3 - Гестационный\n4 - Другое",
        "weight": "Введите новый вес в кг:",
        "height": "Введите новый рост в см:"
    }
    
    await callback.message.answer(
        prompts[field],
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(F.text == "❌ Отменить редактирование")
async def cancel_edit(message: Message):
    if message.from_user.id in edit_temp:
        del edit_temp[message.from_user.id]
    await message.answer(
        "❌ Изменения отменены",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.from_user.id.in_(edit_temp.keys()))
async def process_edit(message: Message):
    user_id = message.from_user.id
    field = edit_temp[user_id]["field"]
    value = message.text
    
    try:
        if field == "name":
            if len(value) < 2 or len(value) > 50:
                raise ValueError("Имя должно быть от 2 до 50 символов")
            update_data = {"name": value}
            
        elif field == "age":
            age = int(value)
            if not 1 <= age <= 120:
                raise ValueError
            update_data = {"age": age}
            
        elif field == "diabetes":
            if value not in {"1", "2", "3", "4"}:
                raise ValueError
            update_data = {"diabetes_type": int(value)}
            
        elif field == "weight":
            weight = float(value.replace(',', '.'))
            if not 10 <= weight <= 300:
                raise ValueError
            update_data = {"weight": weight}
            
        elif field == "height":
            height = float(value.replace(',', '.'))
            if not 50 <= height <= 250:
                raise ValueError
            update_data = {"height": height}
            
        await update_user(user_id, **update_data)
        del edit_temp[user_id]
        
        user = await get_user(user_id)
        await message.answer(
            f"✅ {field.capitalize()} успешно обновлен!\n\n" + get_profile_text(user),
            reply_markup=ReplyKeyboardRemove()
        )
        
    except ValueError as e:
        error_messages = {
            "name": "❌ Некорректное имя! Должно быть от 2 до 50 символов",
            "age": "❌ Некорректный возраст! Введите число от 1 до 120",
            "diabetes": "❌ Выберите вариант из списка (1-4)",
            "weight": "❌ Некорректный вес! Пример: 68.5",
            "height": "❌ Некорректный рост! Пример: 175"
        }
        await message.answer(error_messages[field])