from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


from app.core.config import settings
from app.api.routers import main_router

app = FastAPI(title=settings.app_title)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(main_router)

