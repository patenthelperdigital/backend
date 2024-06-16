from typing import Dict, Sequence, Any, Optional

from sqlalchemy import case, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.crud_base import CRUDBase
from app.models import Ownership, Person
from app.models.filter import FilterTaxNumber
from app.models.patent import Patent
from app.schemas.patent import PatentsStats


class CRUDPatent(CRUDBase):
    def __init__(self):
        super().__init__(Patent)

    async def get_patents_list(
            self,
            session: AsyncSession,
            page: int,
            pagesize: int,
            kind: Optional[int] = None,
            actual: Optional[bool] = None
    ) -> Dict[str, int | list[dict[str, list | int | Any]]]:
        """
        Получает список патентов, упорядоченных по названию.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            page (int): Номер страницы для пагинации.
            pagesize (int): Количество элементов на странице.

        Returns:
            Dict[str, int | list[dict[str, list | int | Any]]]: Список патентов с дополнительной информацией.
        """
        skip = (page - 1) * pagesize
        stmt = (
            select(Patent)
            .outerjoin(Ownership, (Ownership.patent_kind == Patent.kind) & (Ownership.patent_reg_number == Patent.reg_number))
            .outerjoin(Person, Person.tax_number == Ownership.person_tax_number)
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.kind, Patent.reg_number)
            .order_by(Patent.actual.desc())
            .offset(skip)
            .limit(pagesize)
        )

        if kind is not None:
            stmt = stmt.where(Patent.kind == kind)
        if actual is not None:
            stmt = stmt.where(Patent.actual == actual)

        result = await session.execute(stmt)
        patents = result.all()

        patents_list = []
        for patent in patents:
            patent_holders = [
                {
                    "tax_number": ownership.person.tax_number,
                    "full_name": ownership.person.full_name,
                }
                for ownership in patent[0].ownerships
            ]

            patents_list.append({
                **patent[0].__dict__,
                "patent_holders": patent_holders,
            })

        total = await session.execute(
            select(func.count()).select_from(Patent))

        return {
            "total": total.scalar(),
            "items": patents_list,
        }

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
                func.coalesce(func.array_length(func.string_to_array(Patent.author_raw, ', '), 1).label('author_count'), 0)
            )
            .outerjoin(Ownership, (Ownership.patent_kind == Patent.kind) & (Ownership.patent_reg_number == Patent.reg_number))
            .outerjoin(Person, Person.tax_number == Ownership.person_tax_number)
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

    async def get_stats(
        self, session: AsyncSession, filter_id: Optional[int] = None
    ) -> dict:
        """
        Статистика по патентам.

        Args:
        session (AsyncSession): асинхронная сессия базы данных.
        filter_id (Optional[int]): опциональный идентификатор загруженного фильтра по списку ИНН.

        Returns:
            dict: словарь со статистикой.
        """
        stats = {}

        total_patents_stmt = (
            select(func.count()).select_from(Patent)
        )
        if filter_id is not None:
            total_patents_stmt = (
                total_patents_stmt
                .join(Ownership)
                .join(
                    FilterTaxNumber,
                    Ownership.person_tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        total_patents_res = await session.execute(total_patents_stmt)
        stats["total_patents"] = total_patents_res.scalar()

        total_patents_ru_stmt = (
            select(func.count()).select_from(Patent).filter_by(country_code="RU")
        )
        if filter_id is not None:
            total_patents_ru_stmt = (
                total_patents_ru_stmt
                .join(Ownership)
                .join(
                    FilterTaxNumber,
                    Ownership.person_tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        total_patents_ru_res = await session.execute(total_patents_ru_stmt)
        stats["total_ru_patents"] = total_patents_ru_res.scalar()

        total_with_holders_stmt = (
            select(func.count(func.distinct(Patent.kind, Patent.reg_number)))
            .select_from(Patent)
            .join(Ownership)
        )
        if filter_id is not None:
            total_with_holders_stmt = (
                total_with_holders_stmt
                .join(
                    FilterTaxNumber,
                    Ownership.person_tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        total_with_holders_res = await session.execute(total_with_holders_stmt)
        stats["total_with_holders"] = total_with_holders_res.scalar()

        total_ru_with_holders_stmt = (
            select(func.count(func.distinct(Patent.kind, Patent.reg_number)))
            .select_from(Patent)
            .filter_by(country_code="RU")
            .join(Ownership)
        )
        if filter_id is not None:
            total_ru_with_holders_stmt = (
                total_ru_with_holders_stmt
                .join(
                    FilterTaxNumber,
                    Ownership.person_tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        total_ru_with_holders_res = await session.execute(total_ru_with_holders_stmt)
        stats["total_ru_with_holders"] = total_ru_with_holders_res.scalar()

        stats["with_holders_percent"] = int(round(
            100 * stats["total_with_holders"] / stats["total_patents"]))
        stats["ru_with_holders_percent"] = int(round(
            100 * stats["total_ru_with_holders"] / stats["total_ru_patents"]))

        by_author_count_stmt = (
            select(
                case(
                    (Patent.author_count == 0, "0"),
                    (Patent.author_count == 1, "1"),
                    (Patent.author_count <= 5, "2–5"),
                    else_="5+"
                ).label("author_count_group"),
                func.count()
            )
            .select_from(Patent)
            .group_by("author_count_group")
        )
        if filter_id is not None:
            by_author_count_stmt = (
                by_author_count_stmt
                .join(Ownership)
                .join(
                    FilterTaxNumber,
                    Ownership.person_tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        by_author_count_res = await session.execute(by_author_count_stmt)
        stats["by_author_count"] = {
            row[0]: row[1]
            for row in by_author_count_res.all()
        }

        by_patent_kind_stmt = (
            select(Patent.kind, func.count())
            .select_from(Patent)
            .group_by(Patent.kind)
        )
        if filter_id is not None:
            by_patent_kind_stmt = (
                by_patent_kind_stmt
                .join(Ownership)
                .join(
                    FilterTaxNumber,
                    Ownership.person_tax_number == FilterTaxNumber.tax_number
                )
                .filter_by(filter_id=filter_id)
            )
        by_patent_kind_res = await session.execute(by_patent_kind_stmt)
        stats["by_patent_kind"] = {
            res[0]: res[1]
            for res in by_patent_kind_res.all()
        }

        return stats

    async def get_patents_list_with_filter(self, session: AsyncSession, page: int, pagesize: int, filter_id: int) -> list[dict[str, int | list[dict[str, Any]] | Any]]:
        skip = (page - 1) * pagesize
        tax_numbers_stmt = select(FilterTaxNumber.tax_number).where(FilterTaxNumber.filter_id == filter_id)
        tax_numbers_result = await session.execute(tax_numbers_stmt)
        tax_numbers = [row[0] for row in tax_numbers_result.all()]

        stmt = (
            select(Patent)
            .outerjoin(Ownership,
                  (Ownership.patent_kind == Patent.kind) & (Ownership.patent_reg_number == Patent.reg_number))
            .outerjoin(Person, Person.tax_number == Ownership.person_tax_number)
            .where(Person.tax_number.in_(tax_numbers))
            .options(selectinload(Patent.ownerships).selectinload(Ownership.person))
            .group_by(Patent.kind, Patent.reg_number)
            .offset(skip)
            .limit(pagesize)
        )

        result = await session.execute(stmt)
        patents = result.all()

        patents_list = []
        for patent in patents:
            patent_holders = [
                {
                    "tax_number": ownership.person.tax_number,
                    "full_name": ownership.person.full_name,
                }
                for ownership in patent[0].ownerships
            ]

            patents_list.append({
                **patent[0].__dict__,
                "patent_holders": patent_holders,
            })

        total = await session.execute(
            select(func.count())
            .select_from(Patent)
            .outerjoin(Ownership)
            .where(Ownership.person_tax_number.in_(tax_numbers)))

        return {
            "total": total.scalar(),
            "items": patents_list,
        }


patent_crud = CRUDPatent()
