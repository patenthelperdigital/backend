from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.crud_base import CRUDBase
from app.models import Ownership
from app.models.person import Person


class CRUDPerson(CRUDBase):
    def __init__(self):
        super().__init__(Person)

    async def get_persons_list(self, session: AsyncSession, page: int, pagesize: int) -> list[dict[str, list | int | Any]]:
        """
        Получает список персон, упорядоченных по убыванию количества принадлежащих им патентов.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            page (int): Номер страницы для пагинации.
            pagesize (int): Количество элементов на странице.

        Returns:
            List[Dict[str, List | int | Any]]: Список персон с дополнительной информацией.
        """
        skip = (page - 1) * pagesize

        stmt = (
            select(Person)
            .join(Ownership, Ownership.person_tax_number == Person.tax_number)
            .options(selectinload(Person.ownerships).selectinload(Ownership.patent))
            .group_by(Person.tax_number)
            .order_by(func.count(Ownership.patent_reg_number).desc())
            .offset(skip)
            .limit(pagesize)
        )

        result = await session.execute(stmt)
        persons = result.scalars().all()

        persons_list = []
        for person in persons:
            patent_ids = [ownership.patent_reg_number for ownership in person.ownerships]
            persons_list.append({
                **person.__dict__,
                "category": person.category,
                "patent_ids": patent_ids,
                "patent_count": len(patent_ids)
            })

        return persons_list

    async def get_person(self, session: AsyncSession, person_tax_number: str) -> dict[str, Any]:
        """
        Получает персону по идентификатору с дополнительной информацией.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            person_tax_number (str): Идентификатор персоны.

        Returns:
            Dict[str, Any]: Словарь с информацией о персоне, включая список идентификаторов патентов и количество патентов.
        """
        stmt = (
            select(Person, func.count(Ownership.patent_reg_number).label("patent_count"))
            .join(Ownership, Ownership.person_tax_number == Person.tax_number)
            .options(selectinload(Person.ownerships).selectinload(Ownership.patent))
            .group_by(Person.tax_number)
            .where(Person.tax_number == person_tax_number)
        )
        result = await session.execute(stmt)
        person, patent_count = result.unique().one_or_none()

        patent_ids = [ownership.patent_reg_number for ownership in person.ownerships]

        return {
            **person.__dict__,
            "category": person.category,
            "patent_ids": patent_ids,
            "patent_count": patent_count,
        }


person_crud = CRUDPerson()
