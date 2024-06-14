from datetime import date
from enum import IntEnum
from typing import Optional

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
    reg_date: Optional[date]
    appl_date: Optional[date]
    author_raw: Optional[str]
    owner_raw: Optional[str]
    address: Optional[str]
    name: str
    actual: bool
    category: Optional[str]
    subcategory: Optional[str]
    kind: int
    author_count: int
    region: Optional[str]
    city: Optional[str]

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
