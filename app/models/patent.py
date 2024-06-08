from sqlalchemy import Column, Integer, Date, String, Boolean
from sqlalchemy.orm import relationship

from app.core.db import Base


class Patent(Base):
    reg_number = Column(Integer, nullable=False, unique=True, index=True)
    reg_date = Column(Date)
    appl_date = Column(Date)
    author_raw = Column(String(length=150))
    owner_raw = Column(String(length=150))
    address = Column(String)
    name = Column(String, unique=True)
    actual = Column(Boolean, default=False)
    class_ = Column('class', Integer)
    #class_codification = Column(Integer)
    subclass = Column(Integer)
    kind = Column(Integer, nullable=False)

    ownerships = relationship('Ownership', back_populates='patent', cascade="all, delete-orphan")