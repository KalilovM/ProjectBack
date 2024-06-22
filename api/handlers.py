from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from uuid import UUID

from api.models import UserCreate, ShowUser, DeleteUserResponse
from db.dals import UserDAL
from db.session import get_db

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


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)


@user_router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)
