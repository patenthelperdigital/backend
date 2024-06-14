from sqlalchemy import Column, Integer, Date, String, Boolean
from sqlalchemy.orm import relationship

from app.core.db import Base


class Person(Base):
    """
    Модель Person представляет физическое или юридическое лицо, связанное с патентом.

    Атрибуты:
       kind (int): Тип лица.
       tax_number (str): Налоговый номер лица. Уникальный и индексируемый столбец. Первичный ключ.
       full_name (str): Полное имя лица.
       short_name (str): Сокращенное имя лица.
       legal_address (str): Юридический адрес лица.
       fact_address (str): Фактический адрес лица.
       reg_date (Date): Дата регистрации лица.
       active (bool): Флаг активности лица, по умолчанию True.
       category (str): Категория лица.
       ownerships (list[Ownership]): Связь с моделью Ownership, с каскадным удалением.
    """
    kind = Column(Integer, nullable=False)
    tax_number = Column(String, unique=True, index=True, primary_key=True)
    full_name = Column(String)
    short_name = Column(String)
    legal_address = Column(String)
    fact_address = Column(String)
    reg_date = Column(Date)
    active = Column(Boolean, default=True)
    category = Column(String)
    ownerships = relationship('Ownership', back_populates='person', cascade="all, delete-orphan")