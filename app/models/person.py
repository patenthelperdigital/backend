from sqlalchemy import Column, Integer, Date, String, Boolean
from sqlalchemy.orm import relationship

from app.core.db import Base


class Person(Base):
    kind = Column(Integer, nullable=False)
    tax_number = Column(String(length=12), nullable=False, index=True)
    full_name = Column(String(length=150))
    short_name = Column(String(length=80))
    legal_address = Column(String)
    fact_address = Column(String)
    reg_date = Column(Date)
    active = Column(Boolean, default=False)

    ownerships = relationship('Ownership', back_populates='person', cascade="all, delete-orphan")