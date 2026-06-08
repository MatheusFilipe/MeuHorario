from http import HTTPStatus

from meuhorario.schemas import ServicePublic


def test_create_service_user_admin(client, token_admin):
    response = client.post(
        '/services/',
        json={'name': 'test', 'duration': 10, 'price': 39.99},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'test',
        'duration': 10,
        'price': 39.99,
    }


def test_create_service_user_professional(client, token_professional):
    response = client.post(
        '/services/',
        json={'name': 'test', 'duration': 10, 'price': 39.99},
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para criar serviços.'
    }


def test_create_service_user_client(client, token):
    response = client.post(
        '/services/',
        json={'name': 'test', 'duration': 10, 'price': 39.99},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para criar serviços.'
    }


def test_get_services_empty(client):
    response = client.get('/services/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'services': []}


def test_get_services(client, service):
    response = client.get('/services/')

    service_schema = ServicePublic.model_validate(service).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'services': [service_schema]}


def test_get_service(client, service):
    response = client.get(f'/services/{service.id}')

    service = ServicePublic.model_validate(service).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == service


def test_get_service_invalid_id(client):
    response = client.get('/services/67')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Serviço não encontrado.'}


def test_update_service_user_client(client, service, token):
    response = client.patch(
        f'/services/{service.id}',
        json={'name': 'new name'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar serviços.'
    }


def test_update_service_user_professional(client, service, token_professional):
    response = client.patch(
        f'/services/{service.id}',
        json={'name': 'new name'},
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar serviços.'
    }


def test_update_service_user_admin(client, service, token_admin):
    response = client.patch(
        f'/services/{service.id}',
        json={'name': 'new name'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'new name'


def test_update_service_invalid_id(client, token_admin):
    response = client.patch(
        '/services/67',
        json={'name': 'new name'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Serviço não encontrado.'}


def test_delete_service_user_client(client, service, token):
    response = client.delete(
        f'/services/{service.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para deletar serviços.'
    }


def test_delete_service_user_professional(client, service, token_professional):
    response = client.delete(
        f'/services/{service.id}',
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para deletar serviços.'
    }


def test_delete_service_user_admin(client, service, token_admin):
    response = client.delete(
        f'/services/{service.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Serviço deletado.'}


def test_delete_service_invalid_id(client, token_admin):
    response = client.delete(
        '/services/67',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Serviço não encontrado.'}
