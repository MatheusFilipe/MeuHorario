from datetime import date, datetime, time, timedelta
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
    AppointmentUpdate,
    FilterAppointments,
    SelectionResponse,
    WeekSlotsResponse,
)
from meuhorario.security import get_current_user

router = APIRouter(prefix='/appointments', tags=['appointments'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]
AppointmentFilter = Annotated[FilterAppointments, Query()]

business_hours = {
    0: (time(8, 0), time(18, 0)),  # Monday
    1: (time(8, 0), time(18, 0)),  # Tuesday
    2: (time(8, 0), time(18, 0)),  # Wednesday
    3: (time(8, 0), time(18, 0)),  # Thursday
    4: (time(8, 0), time(18, 0)),  # Friday
    5: (time(8, 0), time(16, 0)),  # Saturday
}


async def verify_availability(  # noqa: PLR0913 PLR0917
    session, client, professional, start_time, end_time, id=None
):
    if start_time < datetime.now():
        return HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Não é possível fazer um agendamento em datas passadas.',
        )
    out_of_business_hours_exception = HTTPException(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        detail='Fora do horário de funcionamento.',
    )

    if start_time.weekday() not in business_hours.keys():
        return out_of_business_hours_exception
    business_start, business_end = business_hours[start_time.weekday()]
    if start_time.time() < business_start or end_time.time() > business_end:
        return out_of_business_hours_exception

    client_appointments = await session.scalars(
        select(Appointment).where(Appointment.client_id == client.id)
    )
    for appointment in client_appointments:
        if id == appointment.id:
            pass
        else:
            overlap = max(
                timedelta(0),
                (
                    min(appointment.end_time, end_time)
                    - max(appointment.start_time, start_time)
                ),
            )
            if overlap > timedelta(0):
                return HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='O cliente não tem disponibilidade nesse horário.',
                )

    professional_appointments = await session.scalars(
        select(Appointment).where(
            Appointment.professional_id == professional.id
        )
    )
    for appointment in professional_appointments:
        if id == appointment.id:
            pass
        else:
            overlap = max(
                timedelta(0),
                (
                    min(appointment.end_time, end_time)
                    - max(appointment.start_time, start_time)
                ),
            )
            if overlap > timedelta(0):
                return HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='O profissional não tem '
                    'disponibilidade nesse horário.',
                )
    return None


@router.get(
    '/selection', status_code=HTTPStatus.OK, response_model=SelectionResponse
)
async def selection(user: CurrentUser, session: Session):
    clients = []
    professionals = []

    if user.role == UserRole.client:
        professionals = await session.scalars(
            select(User).where(User.role == UserRole.professional)
        )
    elif user.role == UserRole.professional:
        clients = await session.scalars(
            select(User).where(User.role == UserRole.client)
        )
    elif user.role == UserRole.admin:
        clients = await session.scalars(
            select(User).where(User.role == UserRole.client)
        )
        professionals = await session.scalars(
            select(User).where(User.role == UserRole.professional)
        )

    return {'clients': clients, 'professionals': professionals}


@router.post('/', status_code=HTTPStatus.OK, response_model=AppointmentPublic)
async def create_appointment(  # noqa: PLR0912
    user: CurrentUser,
    appointment_schema: AppointmentSchema,
    session: Session,
):
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

    if appointment_schema.start_time < datetime.now():
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Não é possível fazer um agendamento em datas passadas.',
        )

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

    exception = await verify_availability(
        session, client, professional, start_time, end_time
    )
    if exception is not None:
        raise exception

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
        query = query.filter(Appointment.client_id == filter.client_id)
    if filter.professional_id:
        query = query.filter(
            Appointment.professional_id == filter.professional_id
        )
    if filter.service_id:
        query = query.filter(Appointment.service_id == filter.service_id)

    appointments = await session.scalars(
        query.offset(filter.offset).limit(filter.limit)
    )

    return {'appointments': appointments}


@router.patch(
    '/{appointment_id}',
    status_code=HTTPStatus.OK,
    response_model=AppointmentPublic,
)
async def update_appointment(
    session: Session,
    appointment_id: int,
    schema: AppointmentUpdate,
    user: CurrentUser,
):
    appointment = await session.scalar(
        select(Appointment).where(Appointment.id == appointment_id)
    )

    if not appointment:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Agendamento não encontrado.',
        )

    def update():
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(appointment, key, value)

    forbidden_exception = HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Você não tem permissão para atualizar o agendamento.',
    )

    if user.role == UserRole.admin:
        update()

    elif user.role == UserRole.professional:
        if appointment.professional_id != user.id:
            raise forbidden_exception
        update()

    elif user.role == UserRole.client:
        if appointment.client_id != user.id:
            raise forbidden_exception
        update()

    end_time = appointment.start_time + timedelta(
        minutes=appointment.service.duration
    )
    appointment.end_time = end_time

    exception = await verify_availability(
        session,
        appointment.client,
        appointment.professional,
        appointment.start_time,
        appointment.end_time,
        id=appointment.id,
    )
    if exception is not None:
        raise exception

    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    return appointment


@router.delete(
    '/{appointment_id}', status_code=HTTPStatus.OK, response_model=dict
)
async def delete_appointment(
    appointment_id: int, user: CurrentUser, session: Session
):
    appointment = await session.scalar(
        select(Appointment).where(Appointment.id == appointment_id)
    )

    if not appointment:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Agendamento não encontrado.',
        )

    forbidden_exception = HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Você não tem permissão para deletar o agendamento.',
    )

    if user.role == UserRole.admin:
        pass

    elif user.role == UserRole.professional:
        if appointment.professional != user:
            raise forbidden_exception

    elif user.role == UserRole.client:
        if appointment.client != user:
            raise forbidden_exception

    await session.delete(appointment)
    await session.commit()

    return {'message': 'Agendamento deletado.'}


@router.get(
    '/slots',
    status_code=HTTPStatus.OK,
    response_model=WeekSlotsResponse,
)
async def get_appointments_grade(
    session: Session, filter: AppointmentFilter, user: CurrentUser
):
    client_id = filter.client_id
    professional_id = filter.professional_id
    if user.role == UserRole.client:
        client_id = user.id
    elif user.role == UserRole.professional:
        professional_id = user.id
    elif user.role == UserRole.admin:
        pass

    client = await session.scalar(select(User).where(User.id == client_id))
    if not client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Cliente não encontrado.'
        )
    professional = await session.scalar(
        select(User).where(User.id == professional_id)
    )
    if not professional:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Profissional não encontrado.',
        )
    service = await session.scalar(
        select(Service).where(Service.id == filter.service_id)
    )
    if not service:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Serviço não encontrado.'
        )

    start_time = time(8, 0)
    end_time = time(18, 0)
    start_of_week = date.today()
    end_of_week = start_of_week + timedelta(days=6)

    week_slots = []
    day = start_of_week
    while day <= end_of_week:
        day_slots = []
        current_dt = datetime.combine(day, start_time)
        end_dt = datetime.combine(day, end_time)
        while current_dt < end_dt:
            available = (
                True
                if await verify_availability(
                    session,
                    client,
                    professional,
                    current_dt,
                    current_dt + timedelta(minutes=service.duration),
                )
                is None
                else False
            )
            day_slots.append({
                'start_time': current_dt,
                'available': available,
            })
            current_dt += timedelta(minutes=15)
        week_slots.append({'date': day, 'slots': day_slots})
        day += timedelta(days=1)

    return {'days': week_slots}
