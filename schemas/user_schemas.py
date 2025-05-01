from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, list


class AuthRequest(BaseModel):
    first_name: str
    last_name: str
    user_tg: str
    username_tg: str 


class AuthResponse(BaseModel):
    is_admin: bool
    user_tg: str


class LectureResponse(BaseModel):
    id: int
    title: str
    speaker: str
    date: datetime
    end_time: datetime
    max_seats: int
    remaining_seats: int
    format: str
    conference_link: Optional[HttpUrl] = None
    offline_map_link: Optional[HttpUrl] = None
    offline_photo: Optional[str] = None

    class Config:
        from_attributes = True


