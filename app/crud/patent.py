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

        Returns:
            List[Patent]: Список патентов.
        """
        skip = (page - 1) * pagesize
        stmt = (
            select(
                Patent,
                func.string_agg(Person.short_name, ', ').label("owner_raw"),
                func.count(Patent.author_raw.distinct()).label('author_count')
            )
            .join(Ownership, Ownership.patent_id == Patent.id)
            .join(Person, Person.id == Ownership.person_id)
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.id, Ownership.patent_id)
            .offset(skip)
            .limit(pagesize)
        )
        result = await session.execute(stmt)
        patents = result.all()

        patents_list = []
        for patent, owner_raw, author_count in patents:
            patent_holders = [
                {
                    "id": ownership.person.id,
                    "full_name": ownership.person.full_name,
                    "tax_number": ownership.person.tax_number
                }
                for ownership in patent.ownerships
            ]

            patents_list.append({
                **patent.__dict__,
                "owner_raw": owner_raw,
                "patent_holders": patent_holders,
                "author_count": len(patent.author_raw.split(','))
            })

        return patents_list

    async def get_patent(self, session: AsyncSession, id: int) -> dict:
        """
        Получает патент по идентификатору с дополнительной информацией.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            id (int): Идентификатор патента.

        Returns:
            Dict: Словарь с информацией о патенте, включая список идентификаторов владельцев,
                  количество владельцев и количество авторов.
        """
        stmt = (
            select(
                Patent,
                func.string_agg(Person.short_name, ', ').label("owner_raw"),
                func.count(Patent.author_raw.distinct()).label('author_count')
            )
            .join(Ownership, Ownership.patent_id == Patent.id)
            .join(Person, Person.id == Ownership.person_id)
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.id, Ownership.patent_id)
            .where(Patent.id == id)

        )
        result = await session.execute(stmt)
        patent, owner_raw, author_count = result.one()

        patent_holders = [
            {
                "id": ownership.person.id,
                "full_name": ownership.person.full_name,
                "tax_number": ownership.person.tax_number
            }
            for ownership in patent.ownerships
        ]

        return {
            **patent.__dict__,
            "owner_raw": owner_raw,
            "patent_holders": patent_holders,
            "author_count": len(patent.author_raw.split(','))
        }


patent_crud = CRUDPatent()
