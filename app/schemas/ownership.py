from pydantic import BaseModel


class OwnershipBase(BaseModel):
    patent_id: int
    person_id: int


class OwnershipCreate(OwnershipBase):
    pass


class OwnershipUpdate(OwnershipBase):
    pass


class Ownership(OwnershipBase):
    id: int

    class Config:
        orm_mode = True

