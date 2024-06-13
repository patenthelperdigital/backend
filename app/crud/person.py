from typing import Sequence, Any

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

        Returns:
            List[Person]: Список персон.
        """
        skip = (page - 1) * pagesize

        stmt = (select(Person)
                .options(selectinload(Person.ownerships))
                .join(Ownership, Ownership.person_id == Person.id)
                .group_by(Person.id)
                .order_by(func.count(Ownership.patent_id).desc())
                .offset(skip)
                .limit(pagesize))

        result = await session.execute(stmt)
        persons = result.scalars().all()
        persons_list = []
        for person in persons:
            patent_ids = [ownership.patent_id for ownership in person.ownerships]
            persons_list.append({
                **person.__dict__,
                "category": person.category,
                "patent_ids": patent_ids,
                "patent_count": len(patent_ids)
            })

        return persons_list

    async def get_person(self, session: AsyncSession, id: int) -> dict:
        """
        Получает персону по идентификатору с дополнительной информацией.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            id (int): Идентификатор персоны.

        Returns:
            Dict: Словарь с информацией о персоне, включая список идентификаторов патентов и количество патентов.
        """
        stmt = (
            select(
                Person,
                func.count(Ownership.patent_id).label("patent_count")
            )
            .join(Ownership, Ownership.person_id == Person.id)
            .options(selectinload(Person.ownerships).selectinload(Ownership.patent))
            .group_by(Person.id)
            .where(Person.id == id)
        )
        result = await session.execute(stmt)
        person, patent_count = result.unique().one_or_none()

        patent_ids = [ownership.patent_id for ownership in person.ownerships]

        return {
            **person.__dict__,
            "category": person.category,
            "patent_ids": patent_ids,
            "patent_count": patent_count,
        }





person_crud = CRUDPerson()
