from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meuhorario.database import get_session
from meuhorario.models import Appointment, User, UserRole
from meuhorario.schemas import AppointmentPublic, AppointmentSchema
from meuhorario.security import get_current_user

router = APIRouter(prefix='/appointments', tags=['appointments'])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]


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

        client_id = user.id
        professional_id = professional.id

    elif user.role == UserRole.professional:
        client = await session.scalar(
            select(User).where(User.id == appointment_schema.client_id)
        )
        if not client:
            raise user_not_found()

        if client.role != UserRole.client:
            raise unprocessable_entity(client=True)

        client_id = client.id
        professional_id = user.id

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

        client_id = client.id
        professional_id = professional.id

    appointment = Appointment(
        client_id=client_id,
        professional_id=professional_id,
        service_id=appointment_schema.service_id,
        datetime=appointment_schema.datetime,
    )

    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    return appointment
