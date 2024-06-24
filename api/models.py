import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

LETTER_MATCH_PATTERN = re.compile("^[a-zA-Z]+$")


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowUser(TunedModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    password: str
    is_active: bool


class UserCreate(TunedModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value


class DeleteUserResponse(TunedModel):
    deleted_user_id: uuid.UUID


class UpdateUserResponse(TunedModel):
    update_user_id: uuid.UUID
