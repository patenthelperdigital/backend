from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def check_object_exists(model, object_id: int, session: AsyncSession):
    """
       Проверяет, существует ли объект в базе данных по его идентификатору.

       Args:
           model: Модель SQLAlchemy, для которой нужно проверить существование объекта.
           object_id (int): Идентификатор объекта.
           session (AsyncSession): Асинхронная сессия базы данных.

       Raises:
           HTTPException: Исключение с кодом 404 (Not Found), если объект не найден.

       Returns:
           Объект модели, если он существует.
       """
    get_object = await session.execute(select(model).where(model.id == object_id))
    if get_object is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND
        )
    return get_object.scalars().first()
