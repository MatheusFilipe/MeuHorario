from pydantic import BaseModel, ConfigDict, EmailStr


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

    model_config = ConfigDict(from_attributes=True)


class UserDB(UserPublic):
    password: str


class UserList(BaseModel):
    users: list[UserPublic]
