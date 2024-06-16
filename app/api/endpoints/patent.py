from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_patent_exists
from app.core.db import get_async_session
from app.crud.patent import patent_crud
from app.models import Patent
from app.patent_parser.parser import create_upload_file
from app.schemas.patent import PatentsList, PatentsStats, PatentAdditionalFields, PatentUpdate, PatentDB, PatentCreate

router = APIRouter()


@router.get('/patents', response_model=PatentsList, status_code=HTTPStatus.OK)
async def list_patents(
    page: int = 1,
    pagesize: int = 10,
    filter_id: Optional[int] = None,
    kind: Optional[int] = None,
    actual: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_session),
) -> PatentsList:

    """
    Получить список патентов.

    Args:
        session (AsyncSession): асинхронная сессия базы данных.
        page (int): номер страницы для пагинации.
        pagesize (int): количество элементов на странице.

    Returns:
        List[PatentAdditionalFields]: список патентов с дополнительными полями.
    """
    if filter_id:
        patents_with_filter = await patent_crud.get_patents_list_with_filter(session, page, pagesize, filter_id)
        return patents_with_filter

    patents = await patent_crud.get_patents_list(session, page, pagesize, kind, actual)
    return patents


@router.get('/patents/stats', response_model=PatentsStats, status_code=HTTPStatus.OK)
async def get_patents_stats(
    filter_id: Optional[int] = None,
    session: AsyncSession = Depends(get_async_session)
) -> PatentsStats:
    """
    Получить статистику по патентам.

    Args:
        filter_id (Optional[int]): опциональный идентификатор загруженного фильтра по списку ИНН.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PatentsStats: словарь со статистикой.
    """
    stats = await patent_crud.get_stats(session, filter_id)

    return stats


@router.post('/patents', response_model=PatentDB, status_code=HTTPStatus.CREATED)
async def create_patent(
        patent: PatentCreate,
        session: AsyncSession = Depends(get_async_session)
) -> PatentDB:
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


@router.get('/patents/{patent_kind}/{patent_reg_number}', response_model=PatentAdditionalFields, status_code=HTTPStatus.OK)
async def get_patent(
    patent_kind: int,
    patent_reg_number: int,
    session: AsyncSession = Depends(get_async_session)
) -> PatentAdditionalFields:
    """
    Получить патент по идентификатору.

    Args:
        patent_kind (int): тип патента.
        patent_reg_number (int): регистрационный номер патента.
        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PatentAdditionalFields: патент с дополнительными полями.
    """
    patent = await patent_crud.get_patent(session, patent_kind, patent_reg_number)
    return patent


@router.patch('/patents/{patent_kind}/{patent_reg_number}', response_model=PatentDB, status_code=HTTPStatus.OK)
async def update_patent(
        patent_kind: int,
        patent_reg_number: int,
        obj_in: PatentUpdate,
        session: AsyncSession = Depends(get_async_session)
) -> PatentDB:
    """
    Обновить существующий патент.

    Args:
       patent_kind (int): вид патента.
       patent_reg_number (int): регистрационный номер патента.
       obj_in (PatentUpdate): данные для обновления патента.
       session (AsyncSession): асинхронная сессия базы данных.

    Returns:
       PatentDB: обновленный патент.
    """
    patent = await check_patent_exists(Patent, patent_kind, patent_reg_number, session)
    updated_patent = await patent_crud.update_object(patent, obj_in, session)
    return updated_patent


@router.delete('/patents/{patent_kind}/{patent_reg_number}', status_code=HTTPStatus.NO_CONTENT)
async def delete_patent(
        patent_kind: int,
        patent_reg_number: int,
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удалить патент по виду и регистрационному номеру.

    Args:
        patent_kind (int): вид патента.
        patent_reg_number (int): регистрационный номер патента.
        session (AsyncSession): асинхронная сессия базы данных.
    """
    patent = await check_patent_exists(Patent, patent_kind, patent_reg_number, session)
    await patent_crud.delete_object(patent, session)


@router.post("/uploadfile/", status_code=HTTPStatus.OK)
async def send_patent_file(file: UploadFile):
    """
       Асинхронный путь для загрузки файла Excel с данными о патентах.

       Args:
           file (UploadFile): Загруженный файл Excel.

       Returns:
           Response: Ответ сервера с созданным файлом Excel или сообщением об ошибке.

    """
    await create_upload_file(file)

