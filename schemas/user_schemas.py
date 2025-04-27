from pydantic import BaseModel

class AuthRequest(BaseModel):
    first_name: str
    last_name: str
    user_tg: str
    username_tg: str 

class AuthResponse(BaseModel):
    is_admin: bool
    user_tg: str

