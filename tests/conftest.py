from contextlib import contextmanager
from datetime import date, datetime, time, timedelta

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from meuhorario.app import app
from meuhorario.database import get_session
from meuhorario.models import (
    Appointment,
    Service,
    User,
    UserRole,
    table_registry,
)
from meuhorario.security import get_password_hash
from meuhorario.settings import Settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = factory.Sequence(lambda n: f'teste{n}')
    last_name = factory.Sequence(lambda n: f'sobrenome{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.first_name}@email.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.first_name}.secret')
    role = UserRole.client


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def next_business_day_8am():
    today = date.today()
    match today.weekday():
        case 5:  # Saturday
            days_remaining = 2
        case _:
            days_remaining = 1

    return datetime.combine(
        today + timedelta(days=days_remaining), time(8, 0)
    ).isoformat()


@pytest.fixture
def next_business_day_after_service(next_business_day_8am, service):
    return (
        datetime.fromisoformat(next_business_day_8am)
        + timedelta(minutes=service.duration)
    ).isoformat()


@pytest.fixture
def next_sunday_8am():
    today = date.today()
    days_remaining = 6 - today.weekday()
    if days_remaining == 0:
        days_remaining = 7

    return datetime.combine(
        today + timedelta(days=days_remaining), time(8, 0)
    ).isoformat()


@pytest.fixture
def mock_db_time(next_business_day_8am):
    return (
        lambda *, model, time=datetime.fromisoformat(next_business_day_8am): (
            _mock_db_time(model=model, time=time)
        )
    )


@pytest_asyncio.fixture
async def user(session):
    password = 'secret'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'secret'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def admin(session):
    password = 'secret'
    user = UserFactory(
        password=get_password_hash(password), role=UserRole.admin
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def professional(session):
    password = 'secret'
    user = UserFactory(
        password=get_password_hash(password), role=UserRole.professional
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def service(session):
    service = Service(name='test', duration=10, price=67.67)

    session.add(service)
    await session.commit()
    await session.refresh(service)

    return service


@pytest_asyncio.fixture
async def appointment(
    user, professional, service, session, next_business_day_8am
):
    start_time = datetime.fromisoformat(next_business_day_8am)
    end_time = start_time + timedelta(minutes=service.duration)
    appointment = Appointment(
        client_id=user.id,
        professional_id=professional.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
    )

    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)

    return appointment


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def token_admin(client, admin):
    response = client.post(
        '/auth/token',
        data={'username': admin.email, 'password': admin.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def token_professional(client, professional):
    response = client.post(
        '/auth/token',
        data={
            'username': professional.email,
            'password': professional.clean_password,
        },
    )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()
