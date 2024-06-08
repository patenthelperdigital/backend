from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.crud_base import CRUDBase
from app.models import Ownership
from app.models.patent import Patent


class CRUDPatent(CRUDBase):
    def __init__(self):
        super().__init__(Patent)

    async def get_patents_list(self, session: AsyncSession, page: int) -> Sequence[Patent]:
        """
        Получает список патентов, упорядоченных по названию.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            page (int): Номер страницы для пагинации.

        Returns:
            List[Patent]: Список патентов.
        """
        limit: int = 100
        skip = (page - 1) * limit
        stmt = select(Patent).order_by(Patent.name).offset(skip).limit(limit)
        result = await session.execute(stmt)
        patents = result.scalars().all()
        return patents

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
                func.count(Patent.owner_raw.distinct()).label("person_count"),
                func.count(Patent.author_raw.distinct()).label('author_count')
            )
            .join(Ownership, Ownership.patent_id == Patent.id)
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.id)
            .where(Patent.id == id)
        )
        result = await session.execute(stmt)
        patent, person_count, author_count = result.one()

        person_ids = [ownership.person_id for ownership in patent.ownerships if
                      ownership.person.full_name == patent.owner_raw]

        return {
            **patent.__dict__,
            "person_ids": person_ids,
            "person_count": person_count,
            "author_count": len(patent.author_raw.split(','))
        }


patent_crud = CRUDPatent()
