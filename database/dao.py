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
    async def auth():
        ...