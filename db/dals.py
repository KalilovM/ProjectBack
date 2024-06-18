from sqlalchemy.ext.asyncio.session import AsyncSession
from db.models import User


class UserDAL:
    """Data Access Layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, username:str, email: str, password:str) -> User:
        new_user = User(
            username=username,
            email=email,
            password=password,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user
