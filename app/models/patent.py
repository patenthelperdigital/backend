from sqlalchemy import Column, Integer, Date, String, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base


class Patent(Base):
    """
    Модель Patent представляет патент.

    Атрибуты:
       reg_number (int): Регистрационный номер патента. Индексируемый столбец.
       reg_date (Date): Дата регистрации патента.
       appl_date (Date): Дата подачи заявки на патент.
       author_raw (str): Необработанные данные автора.
       owner_raw (str): Необработанные данные владельца.
       address (str): Адрес связанный с патентом.
       name (str): Название патента.
       actual (bool): Флаг актуальности патента, по умолчанию True.
       category (str): Категория патента.
       subcategory (str): Подкатегория патента.
       kind (int): Тип патента. Не может быть пустым.
       region (str): Регион, связанный с патентом.
       city (str): Город, связанный с патентом.
       author_count (int): Количество авторов патента.
       ownerships (list[Ownership]): Связь с моделью Ownership, с каскадным удалением.

    Ограничения:
       __table_args__: PrimaryKeyConstraint, который связывает поля kind и reg_number.
    """
    reg_number = Column(Integer, nullable=False, index=True)
    reg_date = Column(Date)
    appl_date = Column(Date)
    author_raw = Column(String)
    owner_raw = Column(String)
    address = Column(String)
    name = Column(String)
    actual = Column(Boolean, default=True)
    category = Column(String)
    subcategory = Column(String)
    kind = Column(Integer, nullable=False)
    region = Column(String)
    city = Column(String)
    author_count = Column(Integer)

    ownerships = relationship('Ownership', back_populates='patent', cascade="all, delete-orphan")

    __table_args__ = (
        PrimaryKeyConstraint('kind', 'reg_number'),
        {},
    )

