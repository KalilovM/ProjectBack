from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import UUID, String, Boolean
import uuid


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(40), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)

