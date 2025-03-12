from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.callback_query(F.data == "calendar")
async def show_calendar(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📅 Раздел календаря в разработке")

@router.callback_query(F.data == "charts")
async def show_charts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📈 Раздел графиков в разработке")

@router.callback_query(F.data == "goals")
async def show_goals(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🎯 Раздел целей в разработке")

@router.callback_query(F.data == "achievements")
async def show_achievements(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🏆 Раздел достижений в разработке")