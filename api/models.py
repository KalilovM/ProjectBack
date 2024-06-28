import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from typing import Optional

LETTER_MATCH_PATTERN = re.compile("^[a-zA-Z]+$")


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowUser(TunedModel):
    user_id: uuid.UUID
    username: str
    email: EmailStr
    password: str
    is_active: bool


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Username should contains only letters"
            )
        return value


class UserBaseResponse(BaseModel):
    user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Username should contains only letters"
            )
        return value
