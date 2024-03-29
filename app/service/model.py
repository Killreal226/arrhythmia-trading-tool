from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base, engine


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    figi = Column(String(16))
    ticker = Column(String(8))
    order_time = Column(DateTime, nullable=False)
    price = Column(Float(8))
    volume = Column(Integer)
    direction = Column(String(4))
    account_id = Column(String(16))


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
