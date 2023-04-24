from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession
) -> None:
    if await charity_project_crud.get_project_id_by_name(project_name, session):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
    project_id: int,
    session: AsyncSession
) -> CharityProject:
    charity_project = await charity_project_crud.get_charity_project_by_id(
        project_id, session
    )
    if not charity_project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Project not found'
        )
    return charity_project
