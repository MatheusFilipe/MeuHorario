from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from meuhorario.database import get_session
from meuhorario.models import User
from meuhorario.schemas import UserList, UserPublic, UserSchema

app = FastAPI()
database = list()


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.email == user.email))

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='E-mail já cadastrado.'
        )

    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    return user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(
    session: Session = Depends(get_session), offset: int = 0, limit: int = 10
):
    users = session.scalars(select(User).limit(limit).offset(offset)).all()

    return {'users': users}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    try:
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.email = user.email
        db_user.password = user.password

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='E-mail já cadastrado.'
        )


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=dict
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    session.delete(user)
    session.commit()

    return {'message': 'Usuário deletado.'}
