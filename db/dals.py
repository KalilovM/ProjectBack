from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Union
from uuid import UUID

from sqlalchemy import update, and_
from db.models import User


class UserDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, username: str, email: str, password: str) -> User:
        new_user = User(
            username=username,
            email=email,
            password=password,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        delete_user_id_row = res.fetchone()
        if delete_user_id_row is not None:
            return delete_user_id_row[0]

    async def get_user(self):
        pass
