from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, KeyboardButton
from database.crud import get_user, get_user_records
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import logging

router = Router()
logger = logging.getLogger(__name__)

MAIN_MENU_BUTTONS = [
    ["🩸 Глюкоза", "❤️ Давление"],
    ["⚖️ Вес", "💉 Инсулин"],
    ["🍎 Питание", "💊 Лекарства"],
    ["📊 Статистика", "⚙️ Настройки"],
    ["👤 Мой профиль"]
]

def main_menu():
    builder = ReplyKeyboardBuilder()
    for row in MAIN_MENU_BUTTONS:
        for button in row:
            builder.button(text=button)
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )

def side_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Календарь", callback_data="calendar")
    builder.button(text="📈 Графики", callback_data="charts")
    builder.button(text="🎯 Цели", callback_data="goals")
    builder.button(text="🏆 Достижения", callback_data="achievements")
    builder.adjust(1)
    return builder.as_markup()

@router.message(Command("start"))
async def start(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer(
            "👋 Добро пожаловать! Для начала работы пройдите регистрацию: /register",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    await message.answer(
        "🏠 Главное меню:",
        reply_markup=main_menu()
    )
    await message.answer(
        "📌 Быстрый доступ:",
        reply_markup=side_menu()
    )

@router.message(F.text.in_([btn for row in MAIN_MENU_BUTTONS for btn in row]))
async def handle_menu_buttons(message: types.Message):
    implemented = {
        "👤 Мой профиль": "profile",
        "⚙️ Настройки": "settings",
        "🩸 Глюкоза": "glucose"
    }
    
    if message.text in implemented:
        await message.answer(f"Используйте кнопки меню для работы с разделом")
    else:
        await message.answer("🚧 Раздел в разработке, следите за обновлениями!")

@router.message(Command("help"))
async def show_help(message: types.Message):
    help_text = (
        "ℹ️ Доступные команды:\n"
        "/start - Главное меню\n"
        "/profile - Профиль\n"
        "/register - Регистрация\n"
        "/help - Помощь"
    )
    await message.answer(help_text)
    
@router.message(F.text == "📊 Статистика")
async def show_glucose_stats(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        if not user:
            await message.answer("❌ Сначала пройдите регистрацию!")
            return

        records = await get_user_records(user.id)
        
        if not records:
            await message.answer("📭 У вас пока нет записей о глюкозе")
            return
        
        response = [
            "📈 Ваша статистика за последние замеры:",
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
        ]
        
        for record in records[:10]:
            unit = "ммоль/л" if record.unit == 'mmol/l' else "мг/дл"
            response.append(
                f"🕒 {record.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"🩸 Уровень: {record.value} {unit}\n"
                f"📌 Тип: {record.measurement_type or 'не указан'}\n"
                f"🧪 Кетоны: {record.ketones or '-'}\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
            )
        
        await message.answer("\n".join(response))
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await message.answer("⚠️ Произошла ошибка при загрузке данных")

@router.callback_query(F.data == "charts")
async def show_charts(callback: CallbackQuery):
    buf = None
    try:
        user = await get_user(callback.from_user.id)
        if not user:
            await callback.answer("❌ Сначала пройдите регистрацию!")
            return

        records = await get_user_records(user.id, limit=30)
        
        if not records:
            await callback.answer("📭 Нет данных для построения графика")
            return
        
        unit = "ммоль/л" 
        if records and hasattr(records[0], 'unit'):
            unit = "ммоль/л" if records[0].unit == 'mmol/l' else "мг/дл"

        dates = [r.created_at for r in records]
        values = [float(r.value) for r in records]

        plt.figure(figsize=(12, 6))
        plt.plot(dates, values, marker='o', linestyle='-', color='#2ecc71', linewidth=2)
        plt.title("📊 Динамика уровня глюкозы", fontsize=14, pad=20)
        plt.ylabel(f"Уровень ({unit})", fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d.%m.%Y'))
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        await callback.message.answer_photo(
            buf,
            caption=f"📈 График за последние {len(records)} замеров"
        )
        
    except Exception as e:
        logger.error(f"Ошибка генерации графика: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка при построении графика")
    finally:
        if buf:
            buf.close()