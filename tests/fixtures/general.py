from datetime import date, timedelta
import pytest
from app.server.server import sanic_app
from app.server.server import setup_app
from sanic_testing.reusable import ReusableClient
from app.store.database.gino import db
import asyncio
import typing

if typing.TYPE_CHECKING:
    from sanic import Sanic

@pytest.fixture(scope="session")
def test_app():
    return sanic_app

@pytest.fixture
def cli(test_app)->ReusableClient:
    client = ReusableClient(test_app)
    sanic_app.signal_router.reset()
    setup_app(sanic_app)
    with client:
        run_corootine_in_current_loop(test_app.config["DATABASE"].clear_db())
        yield client


def run_corootine_in_current_loop(corootin):
    curr_loop = asyncio.get_event_loop()
    return curr_loop.run_until_complete(corootin)

@pytest.fixture
def date_today():
    return date.today()

@pytest.fixture
def date_yesterday():
    return date.today()-timedelta(days=1)

