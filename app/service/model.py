from sqlalchemy import Column, Float, Integer, String

from app.database import Base, engine


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    figi = Column(String(16))
    ticker = Column(String(8))
    # order_time =
    price = Column(Float(8))
    quantity = Column(Integer)
    direction = Column(String(4))
    account_id = Column(String(16))
    order_id = Column(String(16))
    order_type = Column(String(8))
    fee = Column(Float(8))


async def create_tables() -> None:
    """Функция создания всез таблиц по моделям, если таких нет"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
