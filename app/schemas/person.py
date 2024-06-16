from enum import IntEnum

from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import date


class PersonKindEnum(IntEnum):
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

    @field_validator('kind')
    @classmethod
    def check_kind_value(cls, value: int):
        if value not in PersonKindEnum.__members__.values():
            raise ValueError('Можно использовать только цифры от 1 до 3')
        return value


class PersonCreate(PersonBase):
    pass


class PersonUpdate(PersonBase):
    pass


class PersonPatents(BaseModel):
    kind: int
    reg_number: int


class PersonAdditionalFields(PersonBase):
    category: str
    patents: list[PersonPatents] = []
    patent_count: int = 0

    class Config:
        orm_mode = True


class PersonDB(PersonBase):
    class Config:
        orm_mode = True


class PersonsList(BaseModel):
    total: int
    items: List[PersonAdditionalFields]
