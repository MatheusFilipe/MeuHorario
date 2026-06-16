from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


class UserRole(str, Enum):
    client = 'client'
    professional = 'professional'
    admin = 'admin'


class AppointmentState(str, Enum): ...


@table_registry.mapped_as_dataclass
class Appointment:
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    professional_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]

    client: Mapped['User'] = relationship(
        init=False,
        foreign_keys=[client_id],
        back_populates='client_appointments',
        lazy='joined',
    )
    professional: Mapped['User'] = relationship(
        init=False,
        foreign_keys=[professional_id],
        back_populates='professional_appointments',
        lazy='joined',
    )
    service: Mapped['Service'] = relationship(
        init=False, back_populates='appointments', lazy='joined'
    )


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

    client_appointments: Mapped[list['Appointment']] = relationship(
        init=False,
        foreign_keys=[Appointment.client_id],
        back_populates='client',
        lazy='selectin',
    )
    professional_appointments: Mapped[list['Appointment']] = relationship(
        init=False,
        foreign_keys=[Appointment.professional_id],
        back_populates='professional',
        lazy='selectin',
    )


@table_registry.mapped_as_dataclass
class Service:
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    duration: Mapped[int]
    price: Mapped[float]

    appointments: Mapped[list['Appointment']] = relationship(
        init=False, back_populates='service', lazy='selectin'
    )
