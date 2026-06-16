from http import HTTPStatus

from meuhorario.models import UserRole


def test_client_create_appointment_invalid_professional_id(
    client, user, service, token
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': 67,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_client_create_appointment_unprocessable_entity(
    client, user, service, token, other_user
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': other_user.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'O usuário não é do tipo profissional.'
    }


def test_client_create_appointment(client, token, user, professional, service):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'client_id': user.id,
        'professional_id': professional.id,
        'service_id': service.id,
        'start_time': '2001-09-11T08:46:00',
        'end_time': '2001-09-11T08:56:00',
    }


def test_professional_create_appointment_invalid_client_id(
    client, professional, service, token_professional
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': 67,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_professional_create_appointment_unprocessable_entity(
    client, professional, service, token_professional, other_user
):
    other_user.role = UserRole.professional

    response = client.post(
        '/appointments/',
        json={
            'client_id': other_user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'O usuário não é do tipo cliente.'}


def test_professional_create_appointment(
    client, token_professional, user, professional, service
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'client_id': user.id,
        'professional_id': professional.id,
        'service_id': service.id,
        'start_time': '2001-09-11T08:46:00',
        'end_time': '2001-09-11T08:56:00',
    }


def test_admin_create_appointment_invalid_client_id(
    client, professional, service, token_admin
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': 67,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Cliente não encontrado.'}


def test_admin_create_appointment_invalid_professional_id(
    client, user, service, token_admin
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': 67,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Profissional não encontrado.'}


def test_admin_create_appointment_unprocessable_entity_client(
    client, professional, service, token_admin, other_user
):
    other_user.role = UserRole.professional

    response = client.post(
        '/appointments/',
        json={
            'client_id': other_user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'O usuário não é do tipo cliente.'}


def test_admin_create_appointment_unprocessable_entity_professional(
    client, user, service, token_admin, other_user
):

    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': other_user.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'O usuário não é do tipo profissional.'
    }


def test_admin_create_appointment(
    client, token_admin, user, professional, service
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'client_id': user.id,
        'professional_id': professional.id,
        'service_id': service.id,
        'start_time': '2001-09-11T08:46:00',
        'end_time': '2001-09-11T08:56:00',
    }


def test_verify_availability_client(  # noqa: PLR0913 PLR0917
    client, appointment, user, professional, service, token
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:50:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'O cliente não tem disponibilidade nesse horário.'
    }


def test_verify_availability_professional(  # noqa: PLR0913 PLR0917
    client, appointment, other_user, professional, service, token_admin
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': other_user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 08:50:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'O profissional não tem disponibilidade nesse horário.'
    }
