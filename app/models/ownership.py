from sqlalchemy import Column, Integer, ForeignKey, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base


class Ownership(Base):
    """
    Модель Ownership представляет связь между патентами и лицами, указывая, кто является владельцем какого патента.

    Атрибуты:
       patent_kind (int): Вид патента. Первичный ключ.
       patent_reg_number (int): Регистрационный номер патента. Первичный ключ.
       person_tax_number (str): Налоговый номер лица. Первичный ключ, внешний ключ к таблице 'person'.
       patent (Patent): Связь с моделью Patent через поля patent_kind и patent_reg_number.
       person (Person): Связь с моделью Person через поле person_tax_number.

    Ограничения:
       __table_args__: ForeignKeyConstraint, который связывает поля patent_kind и patent_reg_number
                       с соответствующими полями в таблице 'patent'.
    """
    patent_kind = Column(Integer, primary_key=True)
    patent_reg_number = Column(Integer, primary_key=True)
    person_tax_number = Column(String, ForeignKey('person.tax_number'), primary_key=True)
    patent = relationship('Patent', back_populates='ownerships')
    person = relationship('Person', back_populates='ownerships')

    __table_args__ = (
        ForeignKeyConstraint(
            ['patent_kind', 'patent_reg_number'],
            ['patent.kind', 'patent.reg_number']
        ),
        {},
    )
