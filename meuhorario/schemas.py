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


class FilterAppointments(FilterPage):
    client_id: int | None = None
    professional_id: int | None = None
    service_id: int | None = None


class ServiceSchema(BaseModel):
    name: str
    duration: int
    price: float


class ServicePublic(ServiceSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceList(BaseModel):
    services: list[ServicePublic]


class ServiceUpdate(BaseModel):
    name: str | None = None
    duration: int | None = None
    price: float | None = None


class AppointmentSchema(BaseModel):
    client_id: int
    professional_id: int
    service_id: int
    start_time: datetime


class AppointmentPublic(AppointmentSchema):
    end_time: datetime
    id: int


class AppointmentList(BaseModel):
    appointments: list[AppointmentPublic]


class AppointmentUpdate(BaseModel):
    service_id: int | None = None
    start_time: datetime | None = None
