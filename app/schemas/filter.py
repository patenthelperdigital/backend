from datetime import datetime

from pydantic import BaseModel


class FilterBase(BaseModel):
    name: str
    filename: str


class FilterCreate(FilterBase):
    pass


class FilterDB(FilterBase):
    id: int
    created: datetime
    tax_numbers_count: int

    class Config:
        orm_mode = True
