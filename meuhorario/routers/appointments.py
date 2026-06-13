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


@router.post('/', status_code=HTTPStatus.OK, response_model=AppointmentPublic)
async def create_appointment(
    client: CurrentUser,
    appointment_schema: AppointmentSchema,
    session: Session,
):
    professional = await session.scalar(
        select(User).where(User.id == appointment_schema.professional_id)
    )

    if not professional:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    if professional.role != UserRole.professional:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='O usuário não é do tipo profissional.',
        )

    appointment = Appointment(
        client_id=client.id,
        professional_id=professional.id,
        service_id=appointment_schema.service_id,
        datetime=appointment_schema.datetime,
    )

    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    return appointment
