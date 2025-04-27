from fastapi import APIRouter, HTTPException
from pydantic import HttpUrl
from database.dao import BaseDAO

import logging
from typing import Optional, List
from schemas.user_schemas import AuthRequest, AuthResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.get('/',
                 response_model=AuthRequest,
                 description='Check type of user',
                 responses={
                     200: {'descr': 'Auth complete'},
                     500: {'descr': 'SERVER ERROR'},}
                 )
async def authenticate(request: AuthRequest):
    logger.info(f'Аутентификация пользователя: telegram_id=')
    try: 
        is_admin = await BaseDAO.check_auth(
            first_name=request.first_name,
            last_name=request.last_name,
            user_tg=request.tg_id,
            username_tg=request.username_tg
        )
    except:
        ...

    

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
