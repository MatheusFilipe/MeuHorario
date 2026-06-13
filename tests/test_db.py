from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from meuhorario.models import User, UserRole


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            first_name='julio',
            last_name='cesar',
            email='juliocesar@email.com',
            password='vivaroma',
            role=UserRole.client,
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(User).where(User.email == 'juliocesar@email.com')
    )

    assert asdict(user) == {
        'id': 1,
        'first_name': 'julio',
        'last_name': 'cesar',
        'email': 'juliocesar@email.com',
        'password': 'vivaroma',
        'created_at': time,
        'role': UserRole.client,
        'client_appointments': [],
        'professional_appointments': [],
    }
