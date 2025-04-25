from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

import logging
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_router = APIRouter()
