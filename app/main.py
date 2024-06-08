from fastapi import FastAPI
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


from app.core.config import settings
from app.api.routers import main_router

app = FastAPI(title=settings.app_title)
app.include_router(main_router)
