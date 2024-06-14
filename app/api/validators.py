from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def check_patent_exists(
        model,
        patent_kind: int,
        patent_reg_number: int,
        session: AsyncSession):
    """
    Проверяет, существует ли патент в базе данных по его типу и регистрационному номеру.

    Args:
        model: Модель SQLAlchemy, для которой нужно проверить существование объекта.
        patent_kind (int): Тип патента.
        patent_reg_number (int): Регистрационный номер патента.
        session (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Исключение с кодом 404 (Not Found), если патент не найден.

    Returns:
        Объект модели, если он существует.
    """
    get_object = await session.execute(select(model).where((model.kind == patent_kind) & (model.reg_number == patent_reg_number)))
    if get_object is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND
        )
    return get_object.scalars().first()


async def check_person_exists(
        model,
        person_tax_number: str,
        session: AsyncSession):
    """
    Проверяет, существует ли персона в базе данных по его налоговому номеру.

    Args:
        model: Модель SQLAlchemy, для которой нужно проверить существование объекта.
        person_tax_number (str): идентификационный номер персоны.
        session (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Исключение с кодом 404 (Not Found), если персона не найдена.

    Returns:
        Объект модели, если он существует.
    """
    get_object = await session.execute(select(model).where(model.tax_number == person_tax_number))
    if get_object is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND
        )
    return get_object.scalars().first()

