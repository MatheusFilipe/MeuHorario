from datetime import date
from http import HTTPStatus

from meuhorario.models import UserRole
from meuhorario.schemas import UserPublic


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


def test_verify_availability_sunday(
    client, user, professional, service, token_admin
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '1972-01-30 15:00:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Fora do horário de funcionamento.'}


def test_verify_availability_out_of_business_hour(
    client, user, professional, service, token_admin
):
    response = client.post(
        '/appointments/',
        json={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 03:00:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Fora do horário de funcionamento.'}


def test_get_appointments_empty(client, token_admin):
    response = client.get(
        '/appointments/',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'appointments': []}


def test_get_appointments_as_admin(client, appointment, token_admin):
    response = client.get(
        '/appointments/',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['appointments']) == 1
    assert (
        response.json()['appointments'][0]['client_id']
        == appointment.client_id
    )
    assert (
        response.json()['appointments'][0]['professional_id']
        == appointment.professional_id
    )


def test_get_appointments_as_client(client, appointment, token):
    response = client.get(
        '/appointments/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['appointments']) == 1
    assert (
        response.json()['appointments'][0]['client_id']
        == appointment.client_id
    )


def test_get_appointments_as_professional(
    client, appointment, token_professional
):
    response = client.get(
        '/appointments/',
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['appointments']) == 1
    assert (
        response.json()['appointments'][0]['professional_id']
        == appointment.professional_id
    )


def test_get_appointments_filter_by_client_id(
    client, appointment, token_admin
):
    response = client.get(
        f'/appointments/?client_id={appointment.client_id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['appointments']) == 1


def test_get_appointments_filter_by_professional_id(
    client, appointment, token_admin
):
    response = client.get(
        f'/appointments/?professional_id={appointment.professional_id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['appointments']) == 1


def test_get_appointments_filter_by_service_id(
    client, appointment, token_admin
):
    response = client.get(
        f'/appointments/?service_id={appointment.service_id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['appointments']) == 1


def test_get_appointments_pagination(client, appointment, token_admin):
    response = client.get(
        '/appointments/?offset=1&limit=1',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'appointments': []}


def test_update_appointment_appointment_not_found(client, token_admin):
    response = client.patch(
        '/appointments/67',
        json={},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Agendamento não encontrado.'}


def test_update_appointment_forbidden_professional(
    client, other_user, appointment
):
    other_user.role = UserRole.professional
    token = client.post(
        '/auth/token',
        data={
            'username': other_user.email,
            'password': other_user.clean_password,
        },
    ).json()['access_token']

    response = client.patch(
        f'/appointments/{appointment.id}',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar o agendamento.'
    }


def test_update_appointment_forbidden_client(client, other_user, appointment):
    token = client.post(
        '/auth/token',
        data={
            'username': other_user.email,
            'password': other_user.clean_password,
        },
    ).json()['access_token']

    response = client.patch(
        f'/appointments/{appointment.id}',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar o agendamento.'
    }


def test_update_appointment_admin(client, appointment, token_admin):
    response = client.patch(
        f'/appointments/{appointment.id}',
        json={'start_time': '2001-09-11 09:03:00'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['end_time'] == '2001-09-11T09:13:00'


def test_update_appointment_professional(
    client, appointment, token_professional
):
    response = client.patch(
        f'/appointments/{appointment.id}',
        json={'start_time': '2001-09-11 09:03:00'},
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['end_time'] == '2001-09-11T09:13:00'


def test_update_appointment_client(client, appointment, token):
    response = client.patch(
        f'/appointments/{appointment.id}',
        json={'start_time': '2001-09-11 09:03:00'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['end_time'] == '2001-09-11T09:13:00'


def test_update_appointment_unavailable(  # noqa: PLR0913 PLR0917
    client, other_user, professional, service, appointment, token_admin
):
    client.post(
        '/appointments/',
        json={
            'client_id': other_user.id,
            'professional_id': professional.id,
            'service_id': service.id,
            'start_time': '2001-09-11 09:03:00',
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    response = client.patch(
        f'/appointments/{appointment.id}',
        json={'start_time': '2001-09-11 09:00:00'},
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'O profissional não tem disponibilidade nesse horário.'
    }


def test_delete_appointment_not_found(client, token_admin):
    response = client.delete(
        '/appointments/67',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Agendamento não encontrado.'}


def test_delete_appointment_forbidden_professional(
    client, other_user, appointment
):
    other_user.role = UserRole.professional
    token = client.post(
        '/auth/token',
        data={
            'username': other_user.email,
            'password': other_user.clean_password,
        },
    ).json()['access_token']

    response = client.delete(
        f'/appointments/{appointment.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para deletar o agendamento.'
    }


def test_delete_appointment_forbidden_client(client, other_user, appointment):
    token = client.post(
        '/auth/token',
        data={
            'username': other_user.email,
            'password': other_user.clean_password,
        },
    ).json()['access_token']

    response = client.delete(
        f'/appointments/{appointment.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para deletar o agendamento.'
    }


def test_delete_appointment(client, appointment, token_admin):
    response = client.delete(
        f'/appointments/{appointment.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Agendamento deletado.'}


def test_selection_as_client(client, professional, token):
    response = client.get(
        '/appointments/selection', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'clients': [],
        'professionals': [
            UserPublic.model_validate(professional).model_dump()
        ],
    }


def test_selection_as_professional(client, user, token_professional):
    response = client.get(
        '/appointments/selection',
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'clients': [UserPublic.model_validate(user).model_dump()],
        'professionals': [],
    }


def test_selection_as_admin(client, user, professional, token_admin):
    response = client.get(
        '/appointments/selection',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'clients': [UserPublic.model_validate(user).model_dump()],
        'professionals': [
            UserPublic.model_validate(professional).model_dump()
        ],
    }


def test_selection_unauthenticated(client):
    response = client.get('/appointments/selection')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_slots_returns_7_days(client, token, professional, service):
    response = client.get(
        '/appointments/slots',
        params={'professional_id': professional.id, 'service_id': service.id},
        headers={'Authorization': f'Bearer {token}'},
    )

    week_length = 7
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['days']) == week_length


def test_slots_sunday_unavailable(client, token, professional, service):
    filter = f'professional_id={professional.id}&service_id={service.id}'
    response = client.get(
        f'/appointments/slots?{filter}',
        headers={'Authorization': f'Bearer {token}'},
    )

    sunday_weekday = 6
    for day in response.json()['days']:
        if date.fromisoformat(day['date']).weekday() == sunday_weekday:
            sunday = day

    assert response.status_code == HTTPStatus.OK
    assert not sunday['slots'][0]['available']


def test_slots_existing_appointment_blocks_slot(
    client, token, appointment, professional, service
):
    filter = f'professional_id={professional.id}&service_id={service.id}'
    response = client.get(
        f'/appointments/slots?{filter}',
        headers={'Authorization': f'Bearer {token}'},
    )

    for day in response.json()['days']:
        if (
            date.fromisoformat(day['date']).weekday()
            == appointment.start_time.weekday()
        ):
            appointment_day = day

    for slot in appointment_day['slots']:
        if slot['start_time'] == appointment.start_time:
            appointment_slot = slot

    assert response.status_code == HTTPStatus.OK
    assert not appointment_slot['available']


def test_slots_as_professional(client, token_professional, user, service):
    response = client.get(
        '/appointments/slots',
        params={'client_id': user.id, 'service_id': service.id},
        headers={'Authorization': f'Bearer {token_professional}'},
    )

    assert response.status_code == HTTPStatus.OK


def test_slots_as_admin(client, token_admin, user, professional, service):
    response = client.get(
        '/appointments/slots',
        params={
            'client_id': user.id,
            'professional_id': professional.id,
            'service_id': service.id,
        },
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
