from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import CharityProject, User
from app.models.utils import get_project_model
from app.schemas.donation import DonationCreate, DonationDB, DonationSuperuser


router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True
)
async def create_new_donation(
    donation: DonationCreate,
    model: CharityProject = Depends(get_project_model),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await donation_crud.create(donation, model, session, user)


@router.get(
    '/',
    response_model=List[DonationSuperuser],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    all_projects = await donation_crud.get_multi(session)
    return all_projects


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude_none=True
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    all_projects = await donation_crud.get_user_donations(session, user)
    return all_projects
