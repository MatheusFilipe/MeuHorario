from http import HTTPStatus


def test_create_appointment_invalid_professional_id(client, service, token):
    response = client.post(
        '/appointments/',
        json={
            'professional_id': 67,
            'service_id': service.id,
            'datetime': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_create_appointment_unprocessable_entity(
    client, service, token, other_user
):
    response = client.post(
        '/appointments/',
        json={
            'professional_id': other_user.id,
            'service_id': service.id,
            'datetime': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'O usuário não é do tipo profissional.'
    }


def test_create_appointment(client, token, user, professional, service):
    response = client.post(
        '/appointments/',
        json={
            'professional_id': professional.id,
            'service_id': service.id,
            'datetime': '2001-09-11 08:46:00',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'client_id': user.id,
        'professional_id': professional.id,
        'service_id': service.id,
        'datetime': '2001-09-11T08:46:00',
    }
