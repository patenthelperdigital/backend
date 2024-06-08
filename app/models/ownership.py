from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db import Base


class Ownership(Base):
    patent_id = Column(Integer, ForeignKey('patent.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    patent = relationship('Patent', back_populates='ownerships')
    person = relationship('Person', back_populates='ownerships')

