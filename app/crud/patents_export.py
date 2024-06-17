from io import BytesIO
from typing import Optional

import pandas as pd
from fastapi import HTTPException

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import StreamingResponse

from app.models import Patent, Person, Ownership
from app.models.filter import FilterTaxNumber


async def get_export_patent_file(
        session: AsyncSession,
        filter_id: Optional[int] = None,
        actual: Optional[str] = None,
        kind: Optional[int] = None,

):
    """
    Получает данные о патентах и экспортирует их в файл XLSX.

    Args:
        session (AsyncSession): Сессия для взаимодействия с базой данных.

        filter_id (Optional[int], optional): Идентификатор фильтра. Если указан, будут экспортированы только
            патенты, связанные с этим фильтром. Если не указан, будут экспортированы первые 10000 патентов.

        actual (Optional[str], optional): Фильтр по актуальности патента. Если "Актуально", будут экспортированы
            только актуальные патенты. Если "Неактуально", будут экспортированы только неактуальные патенты.
            Если не указан, актуальность не будет учитываться.

        kind (Optional[int], optional): Фильтр по виду патента. Если указан, будут экспортированы только патенты
            указанного вида (1 - изобретение, 2 - полезная модель, 3 - промышленный образец).

    Returns:
        StreamingResponse: Поток данных с XLSX-файлом, содержащим информацию о патентах.
        """
    stmt = (
        select(
            Patent.reg_number,
            case(
                (Patent.kind == 1, 'изобретение'),
                (Patent.kind == 2, 'полезная модель'),
                (Patent.kind == 3, 'промышленный образец'),
                else_='неизвестно'
            ).label('patent_kind'),
            Patent.reg_date,
            Patent.name,
            Patent.actual,
            Patent.category,
            Patent.subcategory,
            Patent.region,
            Patent.city,
            func.coalesce(func.array_length(func.string_to_array(Patent.author_raw, ','), 1), 0).label('author_count'),
            Person.tax_number,
            case(
                (Person.kind == 1, 'Юрлицо'),
                (Person.kind == 2, 'Физлицо/ИП'),
                else_='неизвестно'
            ).label('person_kind'),
            Person.category,
            Person.full_name,
        )
        .join(Ownership, (Ownership.patent_kind == Patent.kind) & (Ownership.patent_reg_number == Patent.reg_number))
        .join(Person, Person.tax_number == Ownership.person_tax_number)

    )

    if filter_id is None:
        stmt = stmt.limit(10000)

    if filter_id:
        stmt = stmt.join(FilterTaxNumber, Person.tax_number == FilterTaxNumber.tax_number)
        stmt = stmt.where(FilterTaxNumber.filter_id == filter_id)

    if actual:
        actual_casefold = actual.casefold()
        if actual_casefold == 'актуально':
            stmt = stmt.where(Patent.actual == True)
        elif actual_casefold == "неактуально":
            stmt = stmt.where(Patent.actual == False)
        else:
            raise HTTPException(
                status_code=400,
                detail="Некорректное значение для параметра 'actual'. Ожидается 'актуально' или 'неактуально'."
            )

    if kind:
        stmt = stmt.where(Patent.kind == kind)

    result = await session.execute(stmt)
    patents = result.all()

    data = [
        {
            "ИНН": patent.tax_number,
            "Вид": patent.person_kind,
            "Категория": patent.category,
            "Полное наименование": patent.full_name,
            "Регистрационный номер патента": patent.reg_number,
            "Вид патента": patent.patent_kind,
            "Дата регистрации": patent.reg_date,
            "Название": patent.name,
            "Актуальность патента": patent.actual,
            "Индекс класса по МПК": patent.category,
            "Индекс подкласса по МПК": patent.subcategory,
            "Регион правообладателя": patent.region,
            "Город правообладателя": patent.city,
            "Число авторов": patent.author_count,
        }
        for patent in patents
    ]

    df = pd.DataFrame(data)

    df["Дата регистрации"] = pd.to_datetime(df["Дата регистрации"]).dt.strftime('%d.%m.%Y')

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Patents')

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": "attachment; filename=patents_export.xlsx"}
    )
