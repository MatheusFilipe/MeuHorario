from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


class UserRole(str, Enum):
    client = 'client'
    professional = 'professional'
    admin = 'admin'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[UserRole]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class Schedule:
    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    description: Mapped[str]
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    professional_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    datetime: Mapped[datetime]
    duration: Mapped[int]  # minutes
