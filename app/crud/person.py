from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.crud_base import CRUDBase
from app.models import Ownership
from app.models.person import Person


class CRUDPerson(CRUDBase):
    def __init__(self):
        super().__init__(Person)

    async def get_persons_list(self, session: AsyncSession, page: int) -> Sequence[Person]:
        """
        Получает список персон, упорядоченных по убыванию количества принадлежащих им патентов.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            page (int): Номер страницы для пагинации.

        Returns:
            List[Person]: Список персон.
        """
        limit: int = 100
        skip = (page - 1) * limit

        stmt = (select(Person)
                .join(Ownership, Ownership.person_id == Person.id)
                .group_by(Person.id)
                .order_by(func.count(Ownership.patent_id).desc())
                .offset(skip)
                .limit(limit))

        result = await session.execute(stmt)
        persons = result.scalars().all()
        return persons

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
            "patent_ids": patent_ids,
            "patent_count": patent_count,
        }





person_crud = CRUDPerson()
