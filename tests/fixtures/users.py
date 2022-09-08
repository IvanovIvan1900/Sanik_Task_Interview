import typing
import pytest
from app.users.models import Bill, User
from app.server.server import sanic_app
from .general import run_corootine_in_current_loop
from app.users.auth import get_jwt_token

if typing.TYPE_CHECKING:
    from sanic import Sanic

@pytest.fixture
def dict_user_admin():
    return {
        "login":sanic_app.config["ADMIN_USERNAME"],
        "password":sanic_app.config["ADMIN_PASSWORD"],
        "is_activate": True,
        "is_admin": True,
        "key_activete":"1a7e35ec-9906-47ef-b33f-3ff3de141cdc",
    }

@pytest.fixture
def dict_user_empty_pass():
    return {
        "login":"test login",
        "password":"",
        "is_activate": True,
        "is_admin": False,
        "key_activete":"59ccd952-824f-4146-a0e6-a939601ad674",
    }


@pytest.fixture
def dict_user_1_activate():
    return {
        "login": 'user 1',
        "password":"password_super",
        "is_activate": True,
        "is_admin": False,
        "key_activete":"3422b448-2460-4fd2-9183-8000de6f8343",
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
def dict_bill_one()->dict:
    return {
        "bill_id":1125,
        "amount": 0,
        "user_id":0
    }


@pytest.fixture
def dict_bill_two()->dict:
    return {
        "bill_id":2225,
        "amount": 0,
        "user_id":0
    }

@pytest.fixture
def dict_bill_three()->dict:
    return {
        "bill_id":3325,
        "amount": 0,
        "user_id":0
    }


def get_db_bill_one_for_user(test_app: "Sanic",user:User, dict_bill:dict, amount:int = 0)->Bill:
    dict_data = dict_bill.copy()
    dict_data["user_id"] = user.user_id
    if amount != 0:
        dict_data["amount"] = amount

    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.create_bill_if_not_exist(Bill(**dict_data)))

def create_user_from_dict(test_app: "Sanic", dict_user_data:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_data)))

def get_header_auth_wich_user(user_id:int)->dict:
    if not isinstance(user_id, int):
        raise ValueError("User id must be int")
    token = get_jwt_token(user_id)
    return {'Authorization':f'Basic {token}'}

@pytest.fixture
def db_user_admin(test_app: "Sanic", dict_user_admin:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_admin)))

@pytest.fixture
def db_user_1_activate(test_app: "Sanic", dict_user_1_activate:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_1_activate)))

@pytest.fixture
def db_user_2_non_activate(test_app: "Sanic", dict_user_2_non_activate:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_2_non_activate)))

@pytest.fixture
def db_user_empty_pass(test_app: "Sanic", dict_user_empty_pass:dict)->User:
    return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_empty_pass)))

