from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio.session import AsyncSession

from db.models import User


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

    async def delete_user(self, user_id: UUID) -> UUID | None:
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
        return None

    async def get_user(self, user_id: UUID) -> User | None:
        query = select(User).where(
            and_(User.user_id == user_id, User.is_active == True),
        )
        res = await self.db_session.execute(query)
        show_user = res.fetchone()
        if show_user is not None:
            return show_user[0]
        return None

    async def update_user(self, user_id: UUID, **kwargs) -> UUID | None:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        updated_user = res.fetchone()
        if updated_user is not None:
            return updated_user[0]
        return None
