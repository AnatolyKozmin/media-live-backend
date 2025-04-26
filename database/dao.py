import os
import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import func
from db import async_session_maker
from models import Category, RegCommand, Users, Member, Lectures, LectureRegistrations
from typing import Optional, Dict, Any
from datetime import datetime


class BaseDAO:

    @staticmethod
    async def check_auth(first_name: str, last_name: str, username_tg: str):
        f'''
        Метод, который проверят тип пользователя

        Аргументы:
            - first_name
            - last_name
            - tg_id

        Вохвращает: 
            - True - пользователь админ 
            - False - пользователь обычный
        '''

        async with async_session_maker() as session: 
            ...


    @staticmethod
    async def get_all_lections() -> dict: 
        f'''
        Метод, который собирает все доступные лекции на данный момент  

        Возвращает: 
            - Cписок всех доступных лекций 
        '''
        async with async_session_maker() as session: 
            ...


    @staticmethod
    async def to_register(username_tg: str):
        f'''
        Метод, который регистрирует пользователя на лекцию

        Аргументы: 
            - username_tg

        Возвращает:
            - да ничего не возвращает, он только регестриует и дает код 200
        '''
        async with async_session_maker() as session:
            ...


