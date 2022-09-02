from decimal import Decimal
import typing
import pytest
from app.server.server import sanic_app
from .general import run_corootine_in_current_loop
from app.products.models import ProductModel

if typing.TYPE_CHECKING:
    from sanic import Sanic

@pytest.fixture
def dict_prod_one():
    return {
        "name":"First",
        "description":"",
        "price": '20.00',
    }

@pytest.fixture
def dict_prod_two_wich_description():
    return {
        "name":"Two",
        "description":"Description",
        "price": '100.00',
    }


@pytest.fixture
def dict_prod_three():
    return {
        "name":"Three",
        "description":"Description trhee",
        "price": '5000.00',
    }

@pytest.fixture
def list_dict_prod_count_three(dict_prod_one:dict, dict_prod_two_wich_description:dict, dict_prod_three:dict):
    return [
        dict_prod_one,
        dict_prod_two_wich_description,
        dict_prod_three,
    ]

@pytest.fixture
def list_db_prod_count_three(test_app: "Sanic", list_dict_prod_count_three:list[dict] )->list[ProductModel]:
    return run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.add_list_of_prod(list_dict_prod_count_three))

# def get_header_auth_wich_user(user_id:int)->dict:
#     token = get_jwt_token(user_id)
#     return {'Authorization':f'Basic {token}'}

# @pytest.fixture
# def db_user_admin(test_app: "Sanic", dict_user_admin:dict)->User:
#     return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_admin)))

# @pytest.fixture
# def db_user_1_activate(test_app: "Sanic", dict_user_1_activate:dict)->User:
#     return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_1_activate)))

# @pytest.fixture
# def db_user_2_non_activate(test_app: "Sanic", dict_user_2_non_activate:dict)->User:
#     return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_2_non_activate)))

# @pytest.fixture
# def db_user_empty_pass(test_app: "Sanic", dict_user_empty_pass:dict)->User:
#     return run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.insert_or_find(User(**dict_user_empty_pass)))

