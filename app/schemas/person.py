from enum import Enum

from pydantic import BaseModel
from typing import Optional
from datetime import date


class PersonKindEnum(Enum):
    """
    Перечисление видов лиц:
    1 - юрлицо,
    2 - ИП,
    3 - физлицо.
    """
    LEGAL_ENTITY = 1
    INDIVIDUAL_ENTREPRENEUR = 2
    INDIVIDUAL = 3


class PersonBase(BaseModel):
    kind: int
    tax_number: str
    full_name: Optional[str]
    short_name: Optional[str]
    legal_address: Optional[str]
    fact_address: Optional[str]
    reg_date: Optional[date]
    active: bool


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonAdditionalFields(PersonBase):
    id: int
    patent_ids: list[int] = []
    patent_count: int = 0

    class Config:
        orm_mode = True


class PersonDB(PersonBase):
    id: int

    class Config:
        orm_mode = True
