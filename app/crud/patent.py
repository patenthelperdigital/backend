from typing import Sequence, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.crud_base import CRUDBase
from app.models import Ownership, Person
from app.models.patent import Patent


class CRUDPatent(CRUDBase):
    def __init__(self):
        super().__init__(Patent)

    async def get_patents_list(self, session: AsyncSession, page: int, pagesize: int) -> list[dict[str, int | list[dict[str, Any]] | Any]]:
        """
        Получает список патентов, упорядоченных по названию.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            page (int): Номер страницы для пагинации.
            pagesize (int): Количество элементов на странице.

        Returns:
            List[Dict[str, int | List[Dict[str, Any]] | Any]]: Список патентов с дополнительной информацией.
        """
        skip = (page - 1) * pagesize
        stmt = (
            select(
                Patent,
                func.string_agg(Person.short_name, ', ').label("owner_raw"),
                func.array_length(func.string_to_array(Patent.author_raw, ', '), 1).label('author_count')
            )
            .join(Ownership, (Ownership.patent_kind == Patent.kind) & (Ownership.patent_reg_number == Patent.reg_number))
            .join(Person, Person.tax_number == Ownership.person_tax_number)
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.kind, Patent.reg_number)
            .offset(skip)
            .limit(pagesize)
        )
        result = await session.execute(stmt)
        patents = result.all()

        patents_list = []
        for patent, owner_raw, author_count in patents:
            patent_holders = [
                {
                    "tax_number": ownership.person.tax_number,
                    "full_name": ownership.person.full_name,
                }
                for ownership in patent.ownerships
            ]

            patents_list.append({
                **patent.__dict__,
                "owner_raw": owner_raw,
                "patent_holders": patent_holders,
                "author_count": author_count
            })

        return patents_list

    async def get_patent(self, session: AsyncSession, patent_kind: int, patent_reg_number: int) -> dict[str, Any]:
        """
        Получает патент по идентификатору с дополнительной информацией.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            patent_kind (int): Тип патента.
            patent_reg_number (int): Регистрационный номер патента.

        Returns:
            Dict[str, Any]: Словарь с информацией о патенте, включая список идентификаторов владельцев,
                            количество владельцев и количество авторов.
        """
        stmt = (
            select(
                Patent,
                func.string_agg(Person.short_name, ', ').label("owner_raw"),
                func.array_length(func.string_to_array(Patent.author_raw, ', '), 1).label('author_count')
            )
            .join(Ownership, (Ownership.patent_kind == Patent.kind) & (Ownership.patent_reg_number == Patent.reg_number))
            .join(Person, Person.tax_number == Ownership.person_tax_number)
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.kind, Patent.reg_number)
            .where((Patent.kind == patent_kind) & (Patent.reg_number == patent_reg_number))
        )
        result = await session.execute(stmt)
        patent, owner_raw, author_count = result.one()

        patent_holders = [
            {
                "tax_number": ownership.person.tax_number,
                "full_name": ownership.person.full_name,
            }
            for ownership in patent.ownerships
        ]

        return {
            **patent.__dict__,
            "owner_raw": owner_raw,
            "patent_holders": patent_holders,
            "author_count": author_count
        }


patent_crud = CRUDPatent()
