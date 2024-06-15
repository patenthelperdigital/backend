from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.db import Base


class Filter(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(1000), nullable=False)
    filename = Column(String(1000), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    tax_numbers_count = Column(Integer, nullable=False)

    tax_numbers = relationship('FilterTaxNumber', back_populates='filter', cascade="all, delete")


class FilterTaxNumber(Base):
    id = Column(Integer, primary_key=True, index=True)
    filter_id = Column(Integer, ForeignKey('filter.id'), nullable=False)
    tax_number = Column(Text, nullable=False)

    filter = relationship('Filter', back_populates='tax_numbers')
