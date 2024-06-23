from aiocache import cached, Cache
from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing import Optional

import logging

from app.api.validators import check_person_exists
from app.core.db import get_async_session
from app.crud.person import person_crud
from app.models import Person
from app.schemas.person import (
    PersonsList,
    PersonsStats,
    PersonAdditionalFields,
    PersonCreate,
    PersonDB,
    PersonUpdate,
)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.get(
    "/persons",
    response_model=PersonsList,
    status_code=HTTPStatus.OK
)
@cached(
    ttl=3600,
    cache=Cache.MEMORY,
    key_builder=lambda *args, **kwargs: (
            f"persons:{kwargs.get('page')}:{kwargs.get('pagesize')}:"
            f"{kwargs.get('kind')}:{kwargs.get('active')}:{kwargs.get('category')}")
)
async def list_persons(
        session: AsyncSession = Depends(get_async_session),
        page: int = 1,
        pagesize: int = 10,
        kind: Optional[int] = None,
        active: Optional[bool] = None,
        category: Optional[int] = None
) -> PersonsList:

    """
    Получить список персон.

    Args:
        session (AsyncSession): асинхронная сессия базы данных.
        page (int): номер страницы для пагинации. По умолчанию 1.
        pagesize (int): количество элементов на странице. По умолчанию 10.

    Returns:
        List[PersonAdditionalFields]: список персон с дополнительными полями.
    """
    logger.debug(
        f"Fetching persons with page={page}, pagesize={pagesize}, kind={kind}, active={active}, category={category}")
    try:
        persons = await person_crud.get_persons_list(session, page, pagesize, kind, active, category)
        return persons

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/persons/stats",
    response_model=PersonsStats,
    status_code=HTTPStatus.OK
)
@cached(
    ttl=3600,
    cache=Cache.MEMORY,
    key_builder=lambda *args, **kwargs: (
            f"persons_stats:{kwargs.get('filter_id')}:")
)
async def get_persons_stats(
        filter_id: Optional[int] = None,
        session: AsyncSession = Depends(get_async_session)
) -> PersonsStats:
    """
    Получить статистику по персонам.

    Args:
        filter_id (Optional[int]): опциональный идентификатор загруженного фильтра по списку ИНН.
        Id фильтров начинаются с 4 и выше

        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonsStats: словарь со статистикой.
    """
    logger.debug(
        f"Fetching persons_stats with filter_id={filter_id}")
    try:
        stats = await person_crud.get_stats(session, filter_id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/persons",
    response_model=PersonDB,
    status_code=HTTPStatus.CREATED
)
async def create_person(
        person: PersonCreate,
        session: AsyncSession = Depends(get_async_session)
) -> PersonDB:
    """
    Создать новую персону.

    Args:
        person (PersonCreate): данные для создания новой персоны.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonDB: созданная персона.
    """
    try:
        new_person = await person_crud.create_object(person, session)
        return new_person

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/persons/{person_tax_number}",
    response_model=PersonAdditionalFields,
    status_code=HTTPStatus.OK
)
async def get_person(
        person_tax_number: str,
        session: AsyncSession = Depends(get_async_session)
) -> PersonAdditionalFields:
    """
    Получить персону по идентификатору.

    Args:
        person_tax_number (str): идентификационный номер персоны.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonAdditionalFields: персона с дополнительными полями.
    """
    try:
        person = await person_crud.get_person(session, person_tax_number)
        return person

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    '/persons/{person_tax_number}',
    response_model=PersonDB,
    status_code=HTTPStatus.OK
)
async def update_person(
        person_tax_number: str,
        obj_in: PersonUpdate,
        session: AsyncSession = Depends(get_async_session)
) -> PersonDB:
    """
    Обновить существующую персону.

    Args:
        person_tax_number (str): идентификационный номер персоны.
        obj_in (PersonUpdate): данные для обновления персоны.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonDB: обновленная персона.
    """
    try:
        person = await check_person_exists(Person, person_tax_number, session)
        updated_person = await person_crud.update_object(person, obj_in, session)
        return updated_person

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/persons/{person_tax_number}', status_code=HTTPStatus.NO_CONTENT)
async def delete_person(
        person_tax_number: str,
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удалить персону по идентификатору.

    Args:
        person_tax_number(int): идентификационный номер персоны.
        session (AsyncSession): асинхронная сессия базы данных.
    """
    try:
        person = await check_person_exists(Person, person_tax_number, session)
        await person_crud.delete_object(person, session)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
