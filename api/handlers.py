from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.models import ShowUser, UserCreate, UpdateUserRequest, UserBaseResponse
from db.dals import UserDAL
from db.session import get_db
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


user_router = APIRouter()


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                username=body.username,
                email=body.email,
                password=body.password,
            )
            return ShowUser(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                password=user.password,
                is_active=user.is_active,
            )


async def _delete_user(user_id, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            delete_user_id = await user_dal.delete_user(user_id=user_id)
            return delete_user_id


async def _get_user_by_id(user_id, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user(user_id)
            if user is not None:
                return ShowUser(
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                    is_active=user.is_active,
                    password=user.password,
                )


async def _update_user(
    updated_user_params: dict, user_id: UUID, db
) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            updated_user_id = await user_dal.update_user(
                user_id=user_id, **updated_user_params
            )
            return updated_user_id


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/{user_id}", response_model=UserBaseResponse)
async def delete_user(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> UserBaseResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return UserBaseResponse(user_id=deleted_user_id)


@user_router.get("/{user_id}", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return user


@user_router.patch("/{user_id}", response_model=UserBaseResponse)
async def update_user(
    user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db)
) -> UserBaseResponse:
    updated_user_params = body.dict(exclude_none=True)
    logger.debug(updated_user_params)
    logger.debug(not updated_user_params)
    if not updated_user_params:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    updated_user_id = await _update_user(
        updated_user_params=updated_user_params, db=db, user_id=user_id
    )
    return UserBaseResponse(user_id=updated_user_id)
