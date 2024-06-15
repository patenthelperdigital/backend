from datetime import date
from enum import IntEnum
from typing import List, Optional

from pydantic import BaseModel, field_validator


class KindEnum(IntEnum):
    """
    Перечисление видов патентов:
    1 - изобретение,
    2 - полезная модель,
    3 - промышленный образец.
    """
    INVENTION = 1
    UTILITY_MODEL = 2
    INDUSTRIAL_DESIGN = 3


class PatentHolder(BaseModel):
    full_name: str
    tax_number: str


class PatentBase(BaseModel):
    reg_number: int
    reg_date: Optional[date] = None
    appl_date: Optional[date] = None
    author_raw: Optional[str] = None
    owner_raw: Optional[str] = None
    address: Optional[str] = None
    name: str
    actual: bool
    category: Optional[str] = None
    subcategory: Optional[str] = None
    kind: int
    author_count: int
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None

    @field_validator('kind')
    @classmethod
    def check_kind_value(cls, value: int):
        if value not in KindEnum.__members__.values():
            raise ValueError('Можно использовать только цифры от 1 до 3')
        return value


class PatentCreate(PatentBase):
    pass


class PatentUpdate(PatentBase):
    pass


class PatentAdditionalFields(PatentBase):
    patent_holders: list[PatentHolder]
    author_count: int = 0

    class Config:
        orm_mode = True


class PatentDB(PatentBase):
    class Config:
        orm_mode = True


class PatentsList(BaseModel):
    total: int
    items: List[PatentAdditionalFields]
