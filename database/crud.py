from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import async_session, User, GlucoseRecord

async def create_user(user: User):
    """Создание нового пользователя"""
    async with async_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_user(telegram_id: int) -> User | None:
    """Получение пользователя по Telegram ID"""
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

async def update_user(telegram_id: int, **kwargs):
    """Обновление данных пользователя"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(**kwargs)
        )
        await session.commit()
        
async def create_glucose_record(record: GlucoseRecord):
    """Создание новой записи о глюкозе"""
    async with async_session() as session:
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record
        
async def get_user_records(user_id: int, limit: int = 5):
    """Получение последних записей пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(GlucoseRecord)
            .where(GlucoseRecord.user_id == user_id)
            .order_by(desc(GlucoseRecord.created_at))
            .limit(limit)
        )
        return result.scalars().all()