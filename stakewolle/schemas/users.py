from typing import Optional


from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    username: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    referral_name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    username: str
    password: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    referral_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    is_superuser: Optional[bool] = False
