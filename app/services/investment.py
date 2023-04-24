from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def investment(
    obj_in,
    model,
    session: AsyncSession
):
    models = await session.execute(
        select(model).where(
            model.fully_invested == False  # noqa
        ).order_by(model.id)
    )
    for model in models.scalars().all():
        model_remainder = model.full_amount - model.invested_amount
        object_remainder = obj_in.full_amount - obj_in.invested_amount
        invest_sum = min(model_remainder, object_remainder)
        model.invested_amount += invest_sum
        if model.invested_amount == model.full_amount:
            model.fully_invested = True
            model.close_date = datetime.now()
        obj_in.invested_amount += invest_sum
        if obj_in.invested_amount == obj_in.full_amount:
            obj_in.fully_invested = True
            obj_in.close_date = datetime.now()
            break
