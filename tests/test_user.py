from http import HTTPStatus

from meuhorario.models import UserRole
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
        'role': UserRole.client,
    }


def test_post_user_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'E-mail já cadastrado.'}


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
    response = client.get(f'/users/{user.id}')

    user_schema = UserPublic.model_validate(user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_get_user_invalid_id(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


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
        'role': user.role,
    }


def test_update_integrity_error(client, other_user, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'first_name': 'cristiano',
            'last_name': 'ronaldo',
            'email': other_user.email,
            'password': 'siiiuuuu',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'E-mail já cadastrado.'}


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão.'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado.'}


def test_delete_user_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão.'}


def test_create_user_professional(client, token_admin):
    response = client.post(
        '/users/professional',
        headers={'Authorization': f'Bearer {token_admin}'},
        json={
            'first_name': 'test',
            'last_name': 'test',
            'email': 'professional@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 2,
        'first_name': 'test',
        'last_name': 'test',
        'email': 'professional@example.com',
        'role': UserRole.professional,
    }


def test_create_user_professional_forbidden(client, token):
    response = client.post(
        '/users/professional',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'first_name': 'test',
            'last_name': 'test',
            'email': 'professional@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Apenas administradores podem criar profissionais.'
    }
