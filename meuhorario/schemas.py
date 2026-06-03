from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from meuhorario.models import UserRole


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole = Field(default=UserRole.client)

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=10)


class ScheduleSchema(BaseModel):
    description: str
    client_id: int
    professional_id: int
    datetime: datetime
    duration: int


class SchedulePublic(ScheduleSchema):
    id: int
