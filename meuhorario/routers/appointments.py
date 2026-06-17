from datetime import timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meuhorario.database import get_session
from meuhorario.models import Appointment, Service, User, UserRole
from meuhorario.schemas import (
    AppointmentList,
    AppointmentPublic,
    AppointmentSchema,
    FilterAppointments,
)
from meuhorario.security import get_current_user

router = APIRouter(prefix='/appointments', tags=['appointments'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]
AppointmentFilter = Annotated[FilterAppointments, Query()]


def user_not_found(client=False, professional=False):
    if client:
        return HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Cliente não encontrado.',
        )
    elif professional:
        return HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Profissional não encontrado.',
        )
    return HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='Usuário não encontrado.',
    )


def unprocessable_entity(client=False, professional=False):
    if client:
        return HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='O usuário não é do tipo cliente.',
        )
    elif professional:
        return HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='O usuário não é do tipo profissional.',
        )


async def verify_availability(
    session, client, professional, start_time, end_time
):
    client_appointments = await session.scalars(
        select(Appointment).where(Appointment.client_id == client.id)
    )
    for appointment in client_appointments:
        overlap = max(
            timedelta(0),
            (
                min(appointment.end_time, end_time)
                - max(appointment.start_time, start_time)
            ),
        )
        if overlap > timedelta(0):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='O cliente não tem disponibilidade nesse horário.',
            )

    professional_appointments = await session.scalars(
        select(Appointment).where(
            Appointment.professional_id == professional.id
        )
    )
    for appointment in professional_appointments:
        overlap = max(
            timedelta(0),
            (
                min(appointment.end_time, end_time)
                - max(appointment.start_time, start_time)
            ),
        )
        if overlap > timedelta(0):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='O profissional não tem disponibilidade nesse horário.',
            )


@router.post('/', status_code=HTTPStatus.OK, response_model=AppointmentPublic)
async def create_appointment(
    user: CurrentUser,
    appointment_schema: AppointmentSchema,
    session: Session,
):
    if user.role == UserRole.client:
        professional = await session.scalar(
            select(User).where(User.id == appointment_schema.professional_id)
        )
        if not professional:
            raise user_not_found()
        if professional.role != UserRole.professional:
            raise unprocessable_entity(professional=True)

        client = user

    elif user.role == UserRole.professional:
        client = await session.scalar(
            select(User).where(User.id == appointment_schema.client_id)
        )
        if not client:
            raise user_not_found()

        if client.role != UserRole.client:
            raise unprocessable_entity(client=True)

        professional = user

    elif user.role == UserRole.admin:
        client = await session.scalar(
            select(User).where(User.id == appointment_schema.client_id)
        )
        if not client:
            raise user_not_found(client=True)
        if client.role != UserRole.client:
            raise unprocessable_entity(client=True)

        professional = await session.scalar(
            select(User).where(User.id == appointment_schema.professional_id)
        )
        if not professional:
            raise user_not_found(professional=True)
        if professional.role != UserRole.professional:
            raise unprocessable_entity(professional=True)

    service = await session.scalar(
        select(Service).where(Service.id == appointment_schema.service_id)
    )
    start_time = appointment_schema.start_time
    end_time = appointment_schema.start_time + timedelta(
        minutes=service.duration
    )

    await verify_availability(
        session, client, professional, start_time, end_time
    )

    appointment = Appointment(
        client_id=client.id,
        professional_id=professional.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
    )

    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    return appointment


@router.get('/', status_code=HTTPStatus.OK, response_model=AppointmentList)
async def get_appointments(
    session: Session, user: CurrentUser, filter: AppointmentFilter
):
    if user.role == UserRole.client:
        query = select(Appointment).where(Appointment.client == user)

    elif user.role == UserRole.professional:
        query = select(Appointment).where(Appointment.professional == user)
    elif user.role == UserRole.admin:
        query = select(Appointment)

    if filter.client_id:
        query = query.filter(Appointment.client_id.contains(filter.client_id))
    if filter.professional_id:
        query = query.filter(
            Appointment.professional_id.contains(filter.professional_id)
        )
    if filter.service_id:
        query = query.filter(
            Appointment.service_id.contains(filter.service_id)
        )

    appointments = await session.scalars(
        query.offset(filter.offset).limit(filter.limit)
    )

    return {'appointments': appointments}
