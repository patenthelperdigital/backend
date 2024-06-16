from typing import Any, Dict, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.crud_base import CRUDBase
from app.models import Ownership
from app.models.filter import FilterTaxNumber
from app.models.person import Person


class CRUDPerson(CRUDBase):
    def __init__(self):
        super().__init__(Person)

    CATEGORY_MAPPING = {
        1: "ВУЗ",
        2: "Высокотехнологичные ИТ компании",
        3: "Колледжи",
        4: "Научные организации",
        5: "Прочие организации",
    }

    async def get_persons_list(
            self, session: AsyncSession,
            page: int,
            pagesize: int,
            kind: Optional[int] = None,
            active: Optional[bool] = None,
            category: Optional[int] = None
    ) -> Dict[str, int | list[dict[str, list | int | Any]]]:
        """
        Получает список персон, упорядоченных по убыванию количества принадлежащих им патентов.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            page (int): Номер страницы для пагинации.
            pagesize (int): Количество элементов на странице.

        Returns:
            Dict[str, int | list[dict[str, list | int | Any]]]: Список персон с дополнительной информацией.
        """
        skip = (page - 1) * pagesize

        stmt = (
            select(Person)
            .outerjoin(Ownership, Ownership.person_tax_number == Person.tax_number)
            .options(selectinload(Person.ownerships).selectinload(Ownership.patent))
            .group_by(Person.tax_number)
            .order_by(func.count(Ownership.patent_reg_number).desc())
            .offset(skip)
            .limit(pagesize)
        )
        if kind is not None:
            stmt = stmt.where(Person.kind == kind)
        if active is not None:
            stmt = stmt.where(Person.active == active)
        if category is not None:
            stmt = stmt.where(Person.category == self.CATEGORY_MAPPING.get(category))

        result = await session.execute(stmt)
        persons = result.scalars().all()

        persons_list = []
        for person in persons:
            patents = [
                {
                    "kind": ownership.patent_kind,
                    "reg_number": ownership.patent_reg_number
                }
                for ownership in person.ownerships
            ]
            persons_list.append({
                **person.__dict__,
                "category": person.category,
                "patents": patents,
                "patent_count": len(patents)
            })

        total = await session.execute(
            select(func.count()).select_from(Person))

        return {
            "total": total.scalar(),
            "items": persons_list,
        }

    async def get_stats(
        self, session: AsyncSession, filter_id: Optional[int] = None
    ) -> dict:
        """
        Статистика по персонам.

        Args:
        session (AsyncSession): асинхронная сессия базы данных.
        filter_id (Optional[int]): опциональный идентификатор загруженного фильтра по списку ИНН.

        Returns:
            dict: словарь со статистикой.
        """
        stats = {}

        total_persons_stmt = (
            select(func.count()).select_from(Person)
        )
        if filter_id is not None:
            total_persons_stmt = (
                total_persons_stmt
                .join(
                    FilterTaxNumber,
                    Person.tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        total_persons_res = await session.execute(total_persons_stmt)
        stats["total_persons"] = total_persons_res.scalar()

        by_kind_stmt = (
            select(Person.kind, func.count())
            .select_from(Person)
            .group_by(Person.kind)
        )
        if filter_id is not None:
            by_kind_stmt = (
                by_kind_stmt
                .join(
                    FilterTaxNumber,
                    Person.tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        by_kind_res = await session.execute(by_kind_stmt)
        stats["by_kind"] = {
            res[0]: res[1]
            for res in by_kind_res.all()
        }

        by_category_stmt = (
            select(Person.category, func.count())
            .select_from(Person)
            .group_by(Person.category)
        )
        if filter_id is not None:
            by_category_stmt = (
                by_category_stmt
                .join(
                    FilterTaxNumber,
                    Person.tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        by_category_res = await session.execute(by_category_stmt)
        stats["by_category"] = {
            res[0]: res[1]
            for res in by_category_res.all()
        }

        return stats


    async def get_person(self, session: AsyncSession, person_tax_number: str) -> dict[str, Any]:
        """
        Получает персону по идентификатору с дополнительной информацией.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            person_tax_number (str): Идентификатор персоны.

        Returns:
            Dict[str, Any]: Словарь с информацией о персоне, включая список патентов и количество патентов.
        """
        stmt = (
            select(Person, func.count(Ownership.patent_reg_number).label("patent_count"))
            .outerjoin(Ownership, Ownership.person_tax_number == Person.tax_number)
            .options(selectinload(Person.ownerships).selectinload(Ownership.patent))
            .group_by(Person.tax_number)
            .where(Person.tax_number == person_tax_number)
        )
        result = await session.execute(stmt)
        person, patent_count = result.unique().one_or_none()

        patents = [
            {
                "kind": ownership.patent_kind,
                "reg_number": ownership.patent_reg_number
            }
            for ownership in person.ownerships
        ]

        return {
            **person.__dict__,
            "category": person.category,
            "patents": patents,
            "patent_count": len(patents),
        }


person_crud = CRUDPerson()
