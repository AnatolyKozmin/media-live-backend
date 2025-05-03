from fastapi import APIRouter, HTTPException
from pydantic import HttpUrl
from database.dao import BaseDAO

import logging
from typing import Optional, List
from schemas.user_schemas import AuthRequest, AuthResponse, LectureResponse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.get('/',
                 response_model=AuthRequest,
                 description='Check type of user',
                 responses={
                     200: {'descr': 'Auth complete'},
                     500: {'descr': 'SERVER ERROR'},})
async def authenticate(request: AuthRequest):
    logger.info(f'Аутентификация пользователя: telegram_id=')
    try: 
        is_admin = await BaseDAO.check_auth(
            first_name=request.first_name,
            last_name=request.last_name,
            user_tg=request.tg_id,
            username_tg=request.username_tg
        )

        user_name = f'{request.first_name} {request.last_name}'.strip() or "unknown"

        response = AuthResponse(
            is_admin=is_admin,
            user_name=user_name, 
            tg_id=request.user_tg,
            message="is_admin" if is_admin else "user",
        )

        logger.info(f'Результат аутентификации: tg_id: {request.user_tg}, is admin: {is_admin}')
        return response
    except Exception as e:
        logging.error(f'Ошибка при аутентификации: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Ошибка при аутентификации')
     

@user_router.get('/lections', response_model=list[LectureResponse])
async def get_all_lections():
    f'''
    Получение списка всех людей с количеством оставшивхся мест
    '''
    try: 
        lectures = await BaseDAO.get_all_lectures()
        return lectures 
    except Exception as e:
        logger.error(f'Ошибка при получении списка всех лекций {str(e)}')
        raise HTTPException(status_code=500, detail=f'Ошибка при получении списка всех лекций {str(e)}')


@user_router.get("/profile",)
async def get_score():
    f'''
    Отображение баллов, которые пользователь набрал
    '''
    try: 
        scores = await BaseDAO.
