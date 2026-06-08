from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meuhorario.database import get_session
from meuhorario.models import Service, User, UserRole
from meuhorario.schemas import (
    ServiceList,
    ServicePublic,
    ServiceSchema,
    ServiceUpdate,
)
from meuhorario.security import get_current_user

router = APIRouter(prefix='/services', tags=['services'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.OK, response_model=ServicePublic)
async def create_service(
    service_schema: ServiceSchema, session: Session, user: CurrentUser
):
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para criar serviços.',
        )

    service = Service(**service_schema.model_dump())

    session.add(service)
    await session.commit()
    await session.refresh(service)

    return service


@router.get('/', status_code=HTTPStatus.OK, response_model=ServiceList)
async def get_services(session: Session):
    services = await session.scalars(select(Service))

    return {'services': services}


@router.get(
    '/{service_id}', status_code=HTTPStatus.OK, response_model=ServicePublic
)
async def get_service(service_id: int, session: Session):
    service = await session.scalar(
        select(Service).where(Service.id == service_id)
    )

    if not service:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Serviço não encontrado.'
        )

    return service


@router.patch(
    '/{service_id}', status_code=HTTPStatus.OK, response_model=ServicePublic
)
async def update_service(
    session: Session,
    service_id: int,
    service_schema: ServiceUpdate,
    user: CurrentUser,
):
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar serviços.',
        )

    service = await session.scalar(
        select(Service).where(Service.id == service_id)
    )

    if not service:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Serviço não encontrado.'
        )

    for key, value in service_schema.model_dump(exclude_unset=True).items():
        setattr(service, key, value)

    session.add(service)
    await session.commit()
    await session.refresh(service)

    return service


@router.delete('/{service_id}', status_code=HTTPStatus.OK, response_model=dict)
async def delete_service(service_id: int, user: CurrentUser, session: Session):
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para deletar serviços.',
        )

    service = await session.scalar(
        select(Service).where(Service.id == service_id)
    )

    if not service:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Serviço não encontrado.'
        )

    await session.delete(service)
    await session.commit()

    return {'message': 'Serviço deletado.'}
