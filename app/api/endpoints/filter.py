from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


from typing import List

from app.core.db import get_async_session
from app.crud.filter import filter_crud
from app.schemas.filter import FilterDB, FilterCreate

router = APIRouter()


@router.post("/filter", response_model=FilterDB)
async def create_filter(name: str, file: UploadFile, session: AsyncSession = Depends(get_async_session)):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(status_code=400, detail="Данный формат файла не поддерживается.")

    filter_in = FilterCreate(name=name, filename=file.filename)
    file_bytes = await file.read()
    return await filter_crud.create_filter(session, filter_in, file_bytes)


@router.get("/filters", response_model=List[FilterDB])
async def read_filters(session: AsyncSession = Depends(get_async_session)):
    return await filter_crud.get_filters(session)


@router.get("/filter/{filter_id}", response_model=FilterDB)
async def read_filter(filter_id: int, session: AsyncSession = Depends(get_async_session)):
    db_filter = await filter_crud.get_filter(session, filter_id)
    if not db_filter:
        raise HTTPException(status_code=404, detail=f"Фильтр {filter_id} не найден")
    return db_filter


@router.put("/filter/{filter_id}", response_model=FilterDB)
async def update_filter(filter_id: int, name: str, session: AsyncSession = Depends(get_async_session)):
    return await filter_crud.update_filter_name(session, filter_id, name)


@router.delete("/filter/{filter_id}", response_model=FilterDB)
async def delete_filter(filter_id: int, session: AsyncSession = Depends(get_async_session)):
    return await filter_crud.delete_filter(session, filter_id)
