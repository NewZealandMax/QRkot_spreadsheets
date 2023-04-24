from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_name_duplicate, check_project_exists
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.models.utils import get_donation_model
from app.schemas.charity_project import (
    CharityProjectDB, CharityProjectCreate, CharityProjectUpdate
)


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_new_charity_project(
    project: CharityProjectCreate,
    model: Donation = Depends(get_donation_model),
    session: AsyncSession = Depends(get_async_session),
):
    await check_name_duplicate(project.name, session)
    return await charity_project_crud.create(project, model, session)


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def partial_update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    charity_project = await check_project_exists(
        project_id, session
    )
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    charity_project = await check_project_exists(
        project_id, session
    )
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
