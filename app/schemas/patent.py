from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class KindEnum(Enum):
    """
    Перечисление видов патентов:
    1 - изобретение,
    2 - полезная модель,
    3 - промышленный образец.
    """
    INVENTION = 1
    UTILITY_MODEL = 2
    INDUSTRIAL_DESIGN = 3


class PatentBase(BaseModel):
    reg_number: int
    reg_date: Optional[date]
    appl_date: Optional[date]
    author_raw: Optional[str]
    owner_raw: Optional[str]
    address: Optional[str]
    name: str
    actual: bool
    class_: Optional[int]
    subclass: Optional[int]
    kind: int


class PatentCreate(PatentBase):
    pass


class PatentUpdate(PatentBase):
    pass


class PatentAdditionalFields(PatentBase):
    id: int
    person_ids: list[int] = []
    person_count: int = 0
    author_count: int = 0

    class Config:
        orm_mode = True


class PatentDB(PatentBase):
    id: int

    class Config:
        orm_mode = True
