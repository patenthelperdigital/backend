from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_object_exists
from app.core.db import get_async_session
from app.crud.patent import patent_crud
from app.models import Patent

from app.schemas.patent import PatentAdditionalFields, PatentUpdate, PatentDB, PatentCreate

router = APIRouter()


@router.get('/patents', response_model=list[PatentDB], status_code=HTTPStatus.OK)
async def list_patents(session: AsyncSession = Depends(get_async_session), page: int = 1) -> list[PatentDB]:
    """
    Получить список патентов.

    Args:
        session (AsyncSession): асинхронная сессия базы данных.
        page (int): номер страницы для пагинации.

    Returns:
        List[PatentDB]: список патентов.
    """
    patents = await patent_crud.get_patents_list(session, page=page)
    return patents


@router.post('/patent', response_model=PatentDB, status_code=HTTPStatus.CREATED)
async def create_patent(patent: PatentCreate, session: AsyncSession = Depends(get_async_session)) -> PatentDB:
    """
    Создать новый патент.

    Args:
        patent (PatentCreate): данные для создания нового патента.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PatentDB: созданный патент.
    """
    new_patent = await patent_crud.create_object(patent, session)
    return new_patent


@router.get('/patent/{patent_id}', response_model=PatentAdditionalFields, status_code=HTTPStatus.OK)
async def get_patent(patent_id: int, session: AsyncSession = Depends(get_async_session)) -> PatentAdditionalFields:
    """
    Получить патент по идентификатору.

    Args:
        patent_id (int): идентификатор патента.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PatentAdditionalFields: патент с дополнительными полями.
    """
    patent = await patent_crud.get_patent(session, patent_id)
    return patent


@router.patch('/patent/{patent_id}', response_model=PatentDB, status_code=HTTPStatus.OK)
async def update_patent(
    patent_id: int,
    obj_in: PatentUpdate,
    session: AsyncSession = Depends(get_async_session)
) -> PatentDB:
    """
    Обновить существующий патент.

    Args:
        patent_id (int): идентификатор патента.
        obj_in (PatentUpdate): данные для обновления патента.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PatentDB: обновленный патент.
    """
    patent = await check_object_exists(Patent, patent_id, session)
    updated_patent = await patent_crud.update_object(patent, obj_in, session)
    return updated_patent


@router.delete('/patent/{patent_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_patent(patent_id: int, session: AsyncSession = Depends(get_async_session)) -> None:
    """
    Удалить патент по идентификатору.

    Args:
        patent_id (int): идентификатор патента.
        session (AsyncSession): асинхронная сессия базы данных.
    """
    patent = await check_object_exists(Patent, patent_id, session)
    await patent_crud.delete_object(patent, session)