from datetime import datetime
from http import HTTPStatus
from typing import Optional, List, Dict

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        if db_obj.fully_invested:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Закрытый проект нельзя редактировать!'
            )
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        if (
            'full_amount' in update_data and
            update_data['full_amount'] < obj_data['invested_amount']
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail='Full amount can\'t be less than invested amount'
            )
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if db_obj.full_amount == db_obj.invested_amount:
            db_obj.fully_invested = True
            db_obj.close_date = datetime.now()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        if obj_data['invested_amount'] > 0:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='В проект были внесены средства, не подлежит удалению!'
            )
        else:
            await session.delete(db_obj)
            await session.commit()
        return db_obj

    async def get_charity_project_by_id(
        self,
        project_id: int,
        session: AsyncSession
    ) -> Optional[CharityProject]:
        db_project = await session.execute(
            select(CharityProject).where(
                CharityProject.id == project_id
            )
        )
        return db_project.scalars().first()

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession
    ) -> List[Dict[str, str]]:
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == True  # noqa
            )
        )
        response = [
            {
                'name': project.name,
                'invest_time': project.close_date - project.create_date,
                'description': project.description
            } for project in projects.scalars().all()
        ]
        response.sort(key=lambda x: x['invest_time'])
        for project in response:
            project['invest_time'] = str(project['invest_time'])
        return response


charity_project_crud = CRUDCharityProject(CharityProject)
