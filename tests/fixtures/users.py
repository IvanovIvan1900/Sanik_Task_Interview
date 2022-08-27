import typing
import pytest
from app.users.models import User
from app.server.server import sanic_app
from .general import run_corootine_in_current_loop


if typing.TYPE_CHECKING:
    from sanic import Sanic

@pytest.fixture
def dict_user_admin():
    return {
        "login":sanic_app.config["ADMIN_USERNAME"],
        "password":sanic_app.config["ADMIN_PASSWORD"],
        "is_activate": True,
        "is_admin": True,
        "key_activete":None,
    }

@pytest.fixture
def dict_user_1_activate():
    return {
        "login": 'user 1',
        "password":"password_super",
        "is_activate": True,
        "is_admin": False,
        "key_activete":None,
    }

@pytest.fixture
def dict_user_2_non_activate():
    return {
        "login": 'user 2 (Not active)',
        "password":"password_super",
        "is_activate": False,
        "is_admin": False,
        "key_activete":'448096f0-12b4-11e6-88f1-180373e5e84a',
    }

@pytest.fixture
def db_user_admin(test_app: "Sanic", dict_user_admin:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_admin)))

@pytest.fixture
def db_user_1_activate(test_app: "Sanic", dict_user_1_activate:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_1_activate)))

@pytest.fixture
def db_user_2_non_activate(test_app: "Sanic", dict_user_2_non_activate:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_2_non_activate)))