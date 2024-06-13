from sqlalchemy import Column, Integer, Date, String, Boolean
from sqlalchemy.orm import relationship

from app.core.db import Base


class Person(Base):
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