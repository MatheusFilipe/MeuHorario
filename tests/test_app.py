from http import HTTPStatus

from meuhorario.schemas import UserPublic
from meuhorario.security import create_access_token


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


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'first_name': 'cristiano',
            'last_name': 'ronaldo',
            'email': 'cr7@email.com',
            'password': 'siiiuuuu',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'first_name': 'cristiano',
        'last_name': 'ronaldo',
        'email': 'cr7@email.com',
    }


def test_update_integrity_error(client, user, token):
    client.post(
        '/users/',
        json={
            'first_name': 'michael',
            'last_name': 'jackson',
            'email': 'rusbe@email.com',
            'password': 'hehe',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'first_name': 'cristiano',
            'last_name': 'ronaldo',
            'email': 'rusbe@email.com',
            'password': 'siiiuuuu',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'E-mail já cadastrado.'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado.'}


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar suas credenciais.'
    }


def test_current_user_does_not_exists(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar suas credenciais.'
    }
