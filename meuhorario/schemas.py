from pydantic import BaseModel, EmailStr


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


class UserDB(UserPublic):
    password: str


class UserList(BaseModel):
    users: list[UserPublic]
