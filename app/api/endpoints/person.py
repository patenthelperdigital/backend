from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_object_exists
from app.core.db import get_async_session
from app.crud.person import person_crud
from app.models import Person
from app.schemas.person import PersonDB, PersonCreate, PersonAdditionalFields, PersonUpdate

router = APIRouter()


@router.get("/persons", response_model=list[PersonDB], status_code=HTTPStatus.OK)
async def get_persons(page: int = 1, session: AsyncSession = Depends(get_async_session)) -> list[PersonDB]:
    """
    Получить список персон.

    Args:
        page (int): номер страницы для пагинации. По умолчанию 1.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        List[PersonDB]: список персон.
    """
    persons = await person_crud.get_persons_list(session, page)
    return persons


@router.post("/person", response_model=PersonDB, status_code=HTTPStatus.CREATED)
async def create_person(person: PersonCreate, session: AsyncSession = Depends(get_async_session)) -> PersonDB:
    """
    Создать новую персону.

    Args:
        person (PersonCreate): данные для создания новой персоны.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonDB: созданная персона.
    """
    new_person = await person_crud.create_object(person, session)
    return new_person


@router.get("/person/{person_id}", response_model=PersonAdditionalFields, status_code=HTTPStatus.OK)
async def get_person(person_id: int, session: AsyncSession = Depends(get_async_session)) -> PersonAdditionalFields:
    """
    Получить персону по идентификатору.

    Args:
        person_id (int): идентификатор персоны.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonAdditionalFields: персона с дополнительными полями.
    """
    person = await person_crud.get_person(session, person_id)
    return person


@router.patch('/person/{person_id}', response_model=PersonDB, status_code=HTTPStatus.OK)
async def update_person(
        person_id: int,
        obj_in: PersonUpdate,
        session: AsyncSession = Depends(get_async_session)
) -> PersonDB:
    """
    Обновить существующую персону.

    Args:
        person_id (int): идентификатор персоны.
        obj_in (PersonUpdate): данные для обновления персоны.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PersonDB: обновленная персона.
    """
    person = await check_object_exists(Person, person_id, session)
    updated_person = await person_crud.update_object(person, obj_in, session)
    return updated_person


@router.delete('/person/{person_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_person(person_id: int, session: AsyncSession = Depends(get_async_session)) -> None:
    """
    Удалить персону по идентификатору.

    Args:
        person_id (int): идентификатор персоны.
        session (AsyncSession): асинхронная сессия базы данных.
    """
    person = await check_object_exists(Person, person_id, session)
    await person_crud.delete_object(person, session)