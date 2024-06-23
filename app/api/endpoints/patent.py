import logging
from http import HTTPStatus
from typing import Optional

from aiocache import cached, Cache
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.validators import check_patent_exists
from app.core.db import get_async_session
from app.crud.patent import patent_crud
from app.crud.patents_export import get_export_patent_file
from app.models import Patent
from app.patent_parser.parser import create_upload_file
from app.schemas.patent import (
    PatentAdditionalFields,
    PatentCreate,
    PatentDB,
    PatentUpdate,
    PatentsList,
    PatentsStats,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.get(
    '/patents',
    response_model=PatentsList,
    status_code=status.HTTP_200_OK
)
@cached(
    ttl=3600,
    cache=Cache.MEMORY,
    key_builder=lambda *args, **kwargs: (
            f"patents:{kwargs.get('page')}:{kwargs.get('pagesize')}:"
            f"{kwargs.get('filter_id')}:{kwargs.get('kind')}:{kwargs.get('actual')}"
    )
)
async def list_patents(
        page: int = 1,
        pagesize: int = 10,
        filter_id: Optional[int] = None,
        kind: Optional[int] = None,
        actual: Optional[bool] = None,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Получить список патентов.

    Args:
        session (AsyncSession): асинхронная сессия базы данных.
        page (int): номер страницы для пагинации.
        pagesize (int): количество элементов на странице.

    Returns:
        List[PatentAdditionalFields]: список патентов с дополнительными полями.
    """
    logger.debug(
        f"Fetching patents with page={page}, pagesize={pagesize}, filter_id={filter_id}, kind={kind}, actual={actual}")
    try:
        if filter_id:
            patents_with_filter = await patent_crud.get_patents_list_with_filter(session, page, pagesize, filter_id)
            return patents_with_filter

        patents = await patent_crud.get_patents_list(session, page, pagesize, kind, actual)

        return patents

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    '/patents/stats',
    response_model=PatentsStats,
    status_code=status.HTTP_200_OK
)
@cached(
    ttl=3600,
    cache=Cache.MEMORY,
    key_builder=lambda *args, **kwargs: f"patents_stats:{kwargs.get('filter_id')}"
)
async def get_patents_stats(
        filter_id: Optional[int] = None,
        session: AsyncSession = Depends(get_async_session)
) -> PatentsStats:
    """
    Получить статистику по патентам.

    Args:
        filter_id (Optional[int]): опциональный идентификатор загруженного фильтра по списку ИНН.
        Id фильтров начинаются с 4 и выше

        session (AsyncSession): асинхронная сессия базы данных.

    Returns:
        PatentsStats: словарь со статистикой.
    """
    logger.debug(
        f"Fetching patents_stats with filter_id={filter_id}")
    try:
        stats = await patent_crud.get_stats(session, filter_id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/patents',
    response_model=PatentDB,
    status_code=status.HTTP_201_CREATED
)
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
    try:
        new_patent = await patent_crud.create_object(patent, session)
        return new_patent

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    '/patents/{patent_kind}/{patent_reg_number}',
    response_model=PatentAdditionalFields,
    status_code=status.HTTP_200_OK
)
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
    try:
        patent = await patent_crud.get_patent(session, patent_kind, patent_reg_number)
        return patent

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch(
    '/patents/{patent_kind}/{patent_reg_number}',
    response_model=PatentDB,
    status_code=status.HTTP_200_OK
)
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
    try:
        patent = await check_patent_exists(Patent, patent_kind, patent_reg_number, session)
        updated_patent = await patent_crud.update_object(patent, obj_in, session)
        return updated_patent

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    '/patents/{patent_kind}/{patent_reg_number}',
    status_code=status.HTTP_204_NO_CONTENT
)
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
    try:
        patent = await check_patent_exists(Patent, patent_kind, patent_reg_number, session)
        await patent_crud.delete_object(patent, session)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/uploadfile/", status_code=HTTPStatus.OK)
async def send_patent_file(file: UploadFile):
    """
       Асинхронный путь для загрузки файла Excel с данными о патентах.

       Args:
           file (UploadFile): Загруженный файл Excel.

       Returns:
           Response: Ответ сервера с созданным файлом Excel или сообщением об ошибке.

    """
    return await create_upload_file(file)


@router.get("/patents/export", response_class=StreamingResponse)
async def export_patents(
        filter_id: Optional[int] = None,
        actual: Optional[str] = None,
        kind: Optional[int] = None,
        session: AsyncSession = Depends(get_async_session)
):
    """
   Экспортирует данные о патентах в формате XLSX.

   Параметры:
   - filter_id (Optional[int]): Идентификатор фильтра. Если указан, будут экспортированы только патенты,
     связанные с этим фильтром. Если не указан, будут экспортированы первые 10000 патентов.

     Id фильтров начинаются с 4 и выше

   - actual (Optional[str]): Фильтр по актуальности патента. Если "Актуально", будут экспортированы только
     актуальные патенты. Если "Неактуально", будут экспортированы только неактуальные патенты. Если не указан,
     актуальность не будет учитываться.

   - kind (Optional[int]): Фильтр по виду патента. Если указан, будут экспортированы только патенты
     указанного вида (1 - изобретение, 2 - полезная модель, 3 - промышленный образец).

   - session (AsyncSession): Сессия для взаимодействия с базой данных.

   Возвращает:
   - StreamingResponse: Поток данных с XLSX-файлом, содержащим информацию о патентах.

   Исключения:
   - HTTPException(500): Если произошла ошибка при обработке запроса.
"""
    try:
        return await get_export_patent_file(session, filter_id, actual, kind)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
