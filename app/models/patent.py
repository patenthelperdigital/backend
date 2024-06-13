from sqlalchemy import Column, Integer, Date, String, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base


class Patent(Base):
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

