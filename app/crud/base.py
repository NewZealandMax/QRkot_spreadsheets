from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.services.investment import investment


INITIAL_AMOUNT = 0


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def create(
        self,
        obj_in,
        model,
        session: AsyncSession,
        user: Optional[User] = None
    ):
        obj_in_data = obj_in.dict()
        if user:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        setattr(db_obj, 'invested_amount', INITIAL_AMOUNT)
        session.add(db_obj)
        await investment(db_obj, model, session)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()
