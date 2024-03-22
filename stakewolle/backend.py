import datetime
import os
import pytz
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, Request, HTTPException
from fastapi_users import (
    BaseUserManager,
    exceptions,
    FastAPIUsers,
    IntegerIDMixin,
    models,
    schemas,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from sqlalchemy import select

from stakewolle.engine import async_session_maker, get_user_db
from stakewolle.models.models import User, Referral


load_dotenv()
SECRET = os.getenv('SECRET_KEY', '')

google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
    os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: User, request: Optional[Request] = None,
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")  # noqa: E501

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")  # noqa: E501

    async def get_referral_expiring_date(self, user_dict: dict):
        async with async_session_maker.begin() as session:
            result = await session.execute(
                select(Referral.expires_at).
                where(Referral.referral == user_dict['referral_name']),
            )
            return result.scalars().fetchall()[0]

    async def is_referral_exists(self, user_dict: dict):
        async with async_session_maker.begin() as session:
            result = await session.execute(
                select(Referral).
                where(Referral.referral == user_dict['referral_name']),
            )
            result = result.scalar_one_or_none()
            if result:
                return True
            return False

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        try:
            if user_dict['referral_name'] != '':
                referral_exists = await self.is_referral_exists(user_dict)
                if not referral_exists:
                    raise HTTPException(422, 'Referral does not exists')

                referral_expires_at = await self.get_referral_expiring_date(user_dict)  # noqa: E501
                if datetime.datetime.now(pytz.utc) > referral_expires_at:
                    raise HTTPException(400, 'Referral was expired')
            else:
                user_dict['referral_name'] = None
        except KeyError:
            user_dict['referral_name'] = None

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db)
):
    yield UserManager(user_db)


cookie_transport = CookieTransport(
    cookie_name='cookie_transport',
    cookie_max_age=3600,
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])  # noqa: E501

current_active_user = fastapi_users.current_user(active=True)
