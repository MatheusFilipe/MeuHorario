from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from meuhorario.schemas import UserDB, UserList, UserPublic, UserSchema

app = FastAPI()
database = list()


def valid_id(id):
    if id < 1 or id > len(database):
        raise HTTPException(
            detail='ID inválido.', status_code=HTTPStatus.NOT_ACCEPTABLE
        )

    return True


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

    database.append(user_with_id)

    return user_with_id


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_user(user_id: int):
    if valid_id(user_id):
        return database[user_id - 1]


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users():
    return {'users': database}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if valid_id(user_id):
        user_with_id = UserDB(**user.model_dump(), id=user_id)
        database[user_id - 1] = user_with_id

        return user_with_id


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(user_id: int):
    if valid_id(user_id):
        return database.pop(user_id - 1)
