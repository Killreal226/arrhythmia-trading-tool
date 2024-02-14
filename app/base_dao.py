from loguru import logger
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.database import session


class BaseDAO:
    model = None

    @classmethod
    async def add_one(cls, **kwargs) -> None:
        """Вставка в таблицу одной новой записи
                    Пример вызова функции:
        test_1.add_one(name='Kirill', surname ='Kazakov')
        """
        async with session() as sess:
            try:
                query = insert(cls.model).values(kwargs)
                await sess.execute(query)
                await sess.commit()
            except IntegrityError as e:
                await sess.rollback()
                logger.info(f"error in add_one: {e}")

    @classmethod
    async def add_many(cls, *items) -> None:
        """Вставка в таблицу новых записей, любого количества
                    Пример вызова функции:
        test_1.add_many({"name":"Dasha"}, {"name":"Sasha"})
        """
        async with session() as sess:
            try:
                query = insert(cls.model).values(items)
                await sess.execute(query)
                await sess.commit()
            except IntegrityError as e:
                await sess.rollback()
                logger.info(f"error in add_many: {e}")

    @classmethod
    async def select_all(cls, selected_columns: list = None, limit: int = None) -> list[dict]:
        """Метод получения всех данных из таблицы"""
        async with session() as sess:
            try:
                if selected_columns:
                    stmt = select(*[cls.model.__table__.c[col] for col in selected_columns]).limit(limit)
                else:
                    stmt = select(cls.model.__table__.columns).limit(limit)
                result = await sess.execute(stmt)
                return result.mappings().all()
            except IntegrityError as e:
                logger.info(f"error in select_all: {e}")

    @classmethod
    async def select_with_filters(cls, selected_columns: list = None, limit: int = None, **filter_by) -> list[dict]:
        """Получение всех записей с какими либо фильтрами
                    Пример вызова функции:
        test_1.select_filter(name='Kirill', flag_parsing=0)"""
        async with session() as sess:
            try:
                if selected_columns:
                    quary = (
                        select(*[cls.model.__table__.c[col] for col in selected_columns])
                        .filter_by(**filter_by)
                        .limit(limit)
                    )
                else:
                    quary = select(cls.model.__table__.columns).filter_by(**filter_by).limit(limit)
                result = await sess.execute(quary)
                return result.mappings().all()
            except IntegrityError as e:
                logger.info(f"error in select_filter: {e}")
