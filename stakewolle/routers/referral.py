from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select

from stakewolle.backend import (
    current_active_user,
)
from stakewolle.engine import async_session_maker, engine
from stakewolle.models.models import User, Referral
from stakewolle.schemas.referral import ReferralSchema
from pydantic import EmailStr


router = APIRouter(prefix='/referral', tags=['referral'])


@router.get('/get_by_email/')
async def index(email: EmailStr):
    async with engine.begin() as conn:
        result = await conn.execute(
            select(Referral.referral).
            join(User, Referral.user_id == User.id).
            where(User.email == email),
        )
        result = result.scalars().fetchall()
        if result:
            return {'referral': result}
        return {'message': 'User has no referral'}


@router.get('/get_my_referral/')
async def get_referral(user: User = Depends(current_active_user)):
    async with engine.begin() as conn:
        result = await conn.execute(
            select(Referral).
            where(Referral.user_id == user.id),
        )
        result = result.fetchone()
        if result:
            return {'referral': result.referral, 'expires at': result.expires_at}  # noqa: E501
        return {'message': 'You have no referrals'}


@router.post('/new/')
async def post_referral(
    referral: ReferralSchema,
    user: User = Depends(current_active_user),
):
    async with async_session_maker.begin() as session:
        existing_referral = await session.execute(
            select(Referral).
            where(Referral.user_id == user.id),
        )
        existing_referral = existing_referral.scalars().first()
        if existing_referral:
            raise HTTPException(400, 'You already have a referral')
        new_referral = Referral(
            referral=referral.referral,
            user_id=user.id,
            expires_at=referral.expires_at,
        )
        session.add(new_referral)
        await session.commit()
        return {'message': 'Referral added successfully!', 'object': new_referral}  # noqa: E501


@router.delete('/delete/')
async def delete_referral(user: User = Depends(current_active_user)):
    async with async_session_maker.begin() as session:
        existing_referral = await session.execute(
            select(Referral).
            where(Referral.user_id == user.id),
        )
        existing_referral = existing_referral.scalars().first()
        if not existing_referral:
            raise HTTPException(400, 'You do not have a referral')
        await session.delete(existing_referral)
        await session.commit()
        return {'message': 'Your referral was deleted successfully!'}


@router.get('/get_referrals_by_referrer_id/{id}/')
async def get_referrals_by_referrer_id(id: int):
    async with async_session_maker.begin() as session:
        result = await session.execute(
            select(User.username).
            join(Referral, User.referral_name == Referral.referral).
            where(Referral.user_id == id),
        )
        result = result.scalars().fetchall()
        return {'referrer_id': id, 'referrals': result}
