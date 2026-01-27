from http import HTTPStatus


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


def test_get_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'first_name': 'michael',
                'last_name': 'jackson',
                'email': 'michaeljackson@email.com',
            }
        ]
    }


def test_get_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'first_name': 'michael',
        'last_name': 'jackson',
        'email': 'michaeljackson@email.com',
    }


def test_update_user(client):
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


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'first_name': 'cristiano',
        'last_name': 'ronaldo',
        'email': 'cr7@email.com',
    }


def test_invalid_id(client):
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE
