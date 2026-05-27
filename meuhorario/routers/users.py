from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from meuhorario.database import get_session
from meuhorario.models import User
from meuhorario.schemas import FilterPage, UserList, UserPublic, UserSchema
from meuhorario.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPage = Annotated[FilterPage, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
        select(User).where(User.email == user.email)
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='E-mail já cadastrado.'
        )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user(user_id: int, session: Session):
    user = await session.scalar(
        select(User).where(User.id == user_id)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    return user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def get_users(
    session: Session, filter_users: FilterPage
):
    users = await session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    )

    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Você não tem permissão.'
        )

    try:
        current_user.first_name = user.first_name
        current_user.last_name = user.last_name
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='E-mail já cadastrado.'
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=dict)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Você não tem permissão.'
        )

    session.delete(current_user)
    await session.commit()

    return {'message': 'Usuário deletado.'}
