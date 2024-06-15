from fastapi import APIRouter
from app.api.endpoints import patent_router, person_router, filter_router

main_router = APIRouter()

main_router.include_router(patent_router, tags=['Patents'])
main_router.include_router(person_router, tags=['Persons'])
main_router.include_router(filter_router, tags=['Filters'])