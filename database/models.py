from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, BigInteger, Numeric
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from config import DATABASE_URL
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(50))
    age = Column(Integer)
    diabetes_type = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    username = Column(String(50))
    
class GlucoseRecord(Base):
    __tablename__ = "glucose_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))  # Каскадное удаление
    value = Column(Numeric(4,1), nullable=False)  # Формат X.X (например 6.5)
    unit = Column(String(10), default='mmol/l')   # Единицы измерения
    measurement_type = Column(String(50))         # Тип замера
    ketones = Column(Float)                       # Кетоновые тела
    hba1c = Column(Float)                         # Показатель HbA1c
    mood = Column(String(50))                     # Настроение
    notes = Column(String(500))                   # Примечания
    activity = Column(String(50))                 # Физическая активность
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", backref="glucose_records")

# Остальные модели остаются без изменений
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    calories = Column(Integer)
    carbs = Column(Integer)
    gi = Column(Integer)
    meals = relationship("MealRecord", backref="product")

class WaterRecord(Base):
    __tablename__ = "water_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Integer)
    date = Column(DateTime, default=datetime.now)

class MealRecord(Base):
    __tablename__ = "meal_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    calories = Column(Integer)
    date = Column(DateTime, default=datetime.now)

class UserSettings(Base):
    __tablename__ = "user_settings"
    user_id = Column(Integer, primary_key=True)
    water_goal = Column(Integer, default=2000)
    calorie_goal = Column(Integer, default=2000)

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)