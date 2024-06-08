from app.crud.crud_base import CRUDBase
from app.models.ownership import Ownership


class CRUDOwnership(CRUDBase):
    def __init__(self):
        super().__init__(Ownership)


ownership_crud = CRUDOwnership()
