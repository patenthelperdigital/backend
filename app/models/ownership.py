from sqlalchemy import Column, Integer, ForeignKey, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base


class Ownership(Base):
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
