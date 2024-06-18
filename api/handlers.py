from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from api.models import UserCreate, ShowUser
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


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)
