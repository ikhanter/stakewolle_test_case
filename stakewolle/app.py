import os

from fastapi import FastAPI

from dotenv import load_dotenv
from sqlalchemy import text

from stakewolle.backend import (
    auth_backend,
    fastapi_users,
    google_oauth_client,
)
from stakewolle.engine import engine
from stakewolle.schemas.users import UserCreate, UserRead, UserUpdate
from stakewolle.routers.referral import router as referral_router


load_dotenv()

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(
        auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(
        user_schema=UserRead,
        user_create_schema=UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(
        user_schema=UserRead,
        user_update_schema=UserUpdate,
    ),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        os.getenv('SECRET_KEY'),
    ),
    prefix="/auth/google",
    tags=["auth"],
)

app.include_router(referral_router)


@app.get('/')
async def index():
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT * FROM "user";'))
        return {'message': 'Userlist', 'List': result.scalars().fetchall()}
