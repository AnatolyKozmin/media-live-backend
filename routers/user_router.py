from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

import logging
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.get('/auth')
async def authenticate(name: str, lastname: str, username_tg: str):
    return {"message" : "Прсто заглушка"}


@user_router.get('/lections')
async def get_all_lections():
    return {"message": "Такая же просто заглушка"}


@user_router.get("/lections/regestartion")
async def get_regestration():
    return {"message" : "Ручка записи на лекцию"}


@user_router.get("/lections/get_photo")
async def get_photo_lection(lection_id: int):
    return {"message": "Получение фото марщрута всплывающим окном"}


@user_router.get("/profile")
async def get_score():
    return {"message": "Получение баллов участника, а также его команд"}
