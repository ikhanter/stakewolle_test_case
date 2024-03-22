from typing import List
import datetime

from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTable,
    SQLAlchemyBaseUserTable,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import ForeignKey, DateTime, Boolean, String
from sqlalchemy.ext.declarative import declared_attr


class Base(DeclarativeBase):
    pass


class Referral(Base):
    __tablename__ = 'referral'

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    referral: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc),
    )
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=False,
        unique=True,
    )


class OAuthAccount(SQLAlchemyBaseOAuthAccountTable[int], Base):
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    @declared_attr
    def user_id(cls):
        return mapped_column(
            ForeignKey("user.id", ondelete="cascade"),
            nullable=False,
        )


class User(SQLAlchemyBaseUserTable[int], Base):

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    referral_name: Mapped[str] = mapped_column(
        String,
        ForeignKey('referral.referral'),
        nullable=True,
    )
    referrer: Mapped[str] = relationship(
        'Referral',
        backref='User',
        foreign_keys=[referral_name],
    )
    username: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    oauth_accounts: Mapped[List['OAuthAccount']] = relationship(
        'OAuthAccount',
        lazy='joined',
    )
