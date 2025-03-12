from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.crud import create_glucose_record, get_user
from database.models import GlucoseRecord
from datetime import datetime
from .commands import main_menu

router = Router()

class GlucoseStates(StatesGroup):
    value = State()
    measurement_type = State()
    ketones = State()
    mood = State()
    notes = State()

def measurement_types_kb():
    builder = InlineKeyboardBuilder()
    types = [
        ("🕒 Голодание", "Голодание"),
        ("🍽 До еды", "До еды"),
        ("⏲ После еды", "После еды"),
        ("🕑 После еды (1ч)", "После еды (1ч)"),
        ("🕝 После еды (2ч)", "После еды (2ч)"),
        ("🌙 Во время сна", "Во время сна")
    ]
    for text, data in types:
        builder.button(text=text, callback_data=f"measurement_{data}")
    builder.adjust(1)
    return builder.as_markup()

def mood_kb():
    builder = InlineKeyboardBuilder()
    moods = [
        ("😊 Хорошее", "Хорошее"),
        ("😢 Плохое", "Плохое"),
        ("😐 Нейтральное", "Нейтральное"),
        ("😡 Злое", "Злое"),
        ("😴 Усталое", "Усталое"),
        ("🤒 Болезненное", "Болезненное")
    ]
    for text, data in moods:
        builder.button(text=text, callback_data=f"mood_{data}")
    builder.adjust(2)
    return builder.as_markup()

def cancel_keyboard():
    return ReplyKeyboardBuilder().add(KeyboardButton(text="🚫 Отменить")).adjust(1).as_markup()

@router.message(F.text == "🩸 Глюкоза")
async def start_tracking(message: Message, state: FSMContext):
    await state.set_state(GlucoseStates.value)
    await message.answer(
        "📝 Введите уровень глюкозы (ммоль/л или мг/дл):\n"
        "Пример: 5.4 или 97",
        reply_markup=cancel_keyboard()
    )

@router.message(GlucoseStates.value)
async def process_value(message: Message, state: FSMContext):
    try:
        value = message.text.replace(',', '.')
        if value == "🚫 Отменить":
            await state.clear()
            return await message.answer("❌ Ввод отменён", reply_markup=main_menu())
        
        value = float(value)
        unit = 'mmol/l' if value < 30 else 'mg/dl'  # Автоопределение единиц
        
        await state.update_data(value=value, unit=unit)
        await state.set_state(GlucoseStates.measurement_type)
        await message.answer(
            "⏱ Выберите тип замера:",
            reply_markup=measurement_types_kb()
        )
    except:
        await message.answer("❌ Некорректный формат! Пример: 5.4 или 97")

@router.callback_query(F.data.startswith("measurement_"))
async def process_measurement(callback: CallbackQuery, state: FSMContext):
    measurement_type = callback.data.split("_", 1)[1]
    await state.update_data(measurement_type=measurement_type)
    await state.set_state(GlucoseStates.ketones)
    await callback.message.answer(
        "🧪 Введите уровень кетонов (ммоль/л):",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()

@router.message(GlucoseStates.ketones)
async def process_ketones(message: Message, state: FSMContext):
    if message.text == "🚫 Отменить":
        await state.clear()
        return await message.answer("❌ Ввод отменён", reply_markup=main_menu())
    
    try:
        ketones = float(message.text.replace(',', '.'))
        await state.update_data(ketones=ketones)
    except:
        return await message.answer("❌ Некорректный формат! Пример: 0.7")
    
    await state.set_state(GlucoseStates.mood)
    await message.answer(
        "😊 Оцените своё состояние:",
        reply_markup=mood_kb()
    )

@router.callback_query(F.data.startswith("mood_"))
async def process_mood(callback: CallbackQuery, state: FSMContext):
    mood = callback.data.split("_", 1)[1]
    await state.update_data(mood=mood)
    await state.set_state(GlucoseStates.notes)
    await callback.message.answer(
        "📝 Добавьте комментарий (необязательно):",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()

@router.message(GlucoseStates.notes)
async def process_notes(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user(message.from_user.id)
    
    record = GlucoseRecord(
        user_id=user.id,
        value=data['value'],
        unit=data['unit'],
        measurement_type=data.get('measurement_type'),
        ketones=data.get('ketones'),
        mood=data.get('mood'),
        notes=message.text if message.text != "🚫 Отменить" else None,
        created_at=datetime.now()
    )
    
    await create_glucose_record(record)
    await state.clear()
    
    await message.answer(
        "✅ Данные успешно сохранены!\n"
        f"🩸 Уровень: {data['value']} {data['unit']}\n"
        f"📌 Тип замера: {data.get('measurement_type', 'не указан')}",
        reply_markup=main_menu()
    )