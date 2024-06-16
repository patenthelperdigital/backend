from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.core.db import get_async_session
from app.crud.filter import filter_crud
from app.schemas.filter import FilterDB, FilterCreate

router = APIRouter()


@router.post("/filters", response_model=FilterDB)
async def create_filter(name: str, file: UploadFile, session: AsyncSession = Depends(get_async_session)):
    """
    Создает новый фильтр на основе загруженного Excel-файла.

    Args:
        name (str): Имя нового фильтра.
        file (UploadFile): Загружаемый Excel-файл с данными для фильтра.
        session (AsyncSession): Сессия для взаимодействия с базой данных.

    Raises:
        HTTPException(400): Если формат загруженного файла не поддерживается.
        HTTPException(500): Если произошла ошибка при создании фильтра.

    Returns:
        FilterDB: Созданный фильтр.
    """
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(status_code=400, detail="Данный формат файла не поддерживается.")
    try:
        filter_in = FilterCreate(name=name, filename=file.filename)
        file_bytes = await file.read()
        return await filter_crud.create_filter(session, filter_in, file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters", response_model=List[FilterDB])
async def read_filters(session: AsyncSession = Depends(get_async_session)):
    """
    Получает список всех фильтров.

    Args:
        session (AsyncSession): Сессия для взаимодействия с базой данных.

    Returns:
        List[FilterDB]: Список всех фильтров.
    """
    return await filter_crud.get_filters(session)


@router.get("/filters/{filter_id}", response_model=FilterDB)
async def read_filter(filter_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получает фильтр по его идентификатору.

    Args:
        filter_id (int): Идентификатор фильтра.
        session (AsyncSession): Сессия для взаимодействия с базой данных.

    Raises:
        HTTPException(404): Если фильтр с указанным идентификатором не найден.

    Returns:
        FilterDB: Фильтр с указанным идентификатором.
    """
    db_filter = await filter_crud.get_filter(session, filter_id)
    if not db_filter:
        raise HTTPException(status_code=404, detail=f"Фильтр {filter_id} не найден")
    return db_filter


@router.put("/filters/{filter_id}", response_model=FilterDB)
async def update_filter(filter_id: int, name: str, session: AsyncSession = Depends(get_async_session)):
    """
    Обновляет имя существующего фильтра.

    Args:
        filter_id (int): Идентификатор фильтра.
        name (str): Новое имя фильтра.
        session (AsyncSession): Сессия для взаимодействия с базой данных.

    Returns:
        FilterDB: Обновленный фильтр.
    """
    return await filter_crud.update_filter_name(session, filter_id, name)


@router.delete("/filters/{filter_id}", response_model=FilterDB)
async def delete_filter(filter_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Удаляет существующий фильтр.

    Args:
        filter_id (int): Идентификатор фильтра.
        session (AsyncSession): Сессия для взаимодействия с базой данных.

    Returns:
        FilterDB: Удаленный фильтр.
    """
    return await filter_crud.delete_filter(session, filter_id)