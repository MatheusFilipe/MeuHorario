from http import HTTPStatus

from meuhorario.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'first_name': 'michael',
            'last_name': 'jackson',
            'email': 'michaeljackson@email.com',
            'password': 'rusbe',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'first_name': 'michael',
        'last_name': 'jackson',
        'email': 'michaeljackson@email.com',
    }


def test_get_users_with_user(client, user):
    response = client.get('/users/')

    user_schema = UserPublic.model_validate(user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_get_users_empty(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_user(client, user):
    response = client.get('/users/1')

    user_schema = UserPublic.model_validate(user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'first_name': 'cristiano',
            'last_name': 'ronaldo',
            'email': 'cr7@email.com',
            'password': 'siiiuuuu',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'first_name': 'cristiano',
        'last_name': 'ronaldo',
        'email': 'cr7@email.com',
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado.'}
