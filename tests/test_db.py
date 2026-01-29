from dataclasses import asdict
from sqlalchemy import select

from meuhorario.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            first_name='julio',
            last_name='cesar',
            email='juliocesar@email.com',
            password='vivaroma'
        )
    session.add(new_user)
    session.commit()

    user = session.scalar(
        select(User).where(User.email == 'juliocesar@email.com')
    )

    assert asdict(user) == {
        'id': 1,
        'first_name': 'julio',
        'last_name': 'cesar',
        'email': 'juliocesar@email.com',
        'password': 'vivaroma',
        'created_at': time
    }
