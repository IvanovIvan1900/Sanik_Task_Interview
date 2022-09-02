from decimal import Decimal
import json
from operator import itemgetter
import typing

import pytest
from app.products.models import ProductModel
from app.users.models import User
from sanic import Sanic
from tests.fixtures.users import get_header_auth_wich_user
from tests.fixtures.general import run_corootine_in_current_loop

if typing.TYPE_CHECKING:
    from sanic_testing.reusable import ReusableClient

class TestProducts:

    def test_unauthorized(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict]):
        url = test_app.url_for('products')
        _, response = cli.post(url)
        assert 401 == response.status

    def test_post_list_create_and_update(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict], db_user_admin:User):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        url = test_app.url_for('products')
        data = json.dumps({"items":list_dict_prod_count_three})
        _, response = cli.post(url, headers=headers, data=data)
        assert 200 == response.status

        list_db_before = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_of_dict_before = sorted([elem.__dict__['__values__'] for elem in list_db_before], key=itemgetter("prod_id"))

        assert list_of_dict_before == sorted(response.json["list_items"], key=itemgetter("prod_id"))

        new_dict = list_dict_prod_count_three.copy()
        new_dict[1]["description"] = "new description"
        new_dict[2]["description"] = "new description for elem 3"
        new_dict[2]["price"] = '5'

        data = json.dumps({"items":new_dict})
        _, response = cli.post(url, headers=headers, data=data)
        assert 200 == response.status

        list_db_after = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_of_dict_after = sorted([elem.__dict__['__values__'] for elem in list_db_after], key=itemgetter("prod_id"))

        list_of_dict_before[1]["description"] = "new description"
        list_of_dict_before[2]["description"] = "new description for elem 3"
        list_of_dict_before[2]["price"] = Decimal('5')

        assert list_of_dict_before == list_of_dict_after

    def test_post_list_product_wich_empty_array(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict], db_user_admin:User):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        url = test_app.url_for('products')
        data = json.dumps({"items":[]})
        _, response = cli.post(url, headers=headers, data=data)
        assert 200 == response.status

    def test_get_list_products(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict],
                 db_user_admin:User, list_db_prod_count_three:list[ProductModel]):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        url = test_app.url_for('products')
        _, response = cli.get(url, headers=headers)
        assert 200 == response.status

        list_db = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_of_dict = sorted([elem.__dict__['__values__'] for elem in list_db], key=itemgetter("prod_id"))

        assert list_of_dict == sorted(response.json["list_items"], key=itemgetter("prod_id"))

    def test_delete_items(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict],
                 db_user_admin:User, list_db_prod_count_three:list[ProductModel]):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        list_db_before = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_dict_before = [list_db_before[2].__dict__['__values__']]
        url = test_app.url_for('products', **{"list_id":[list_db_before[1].prod_id, list_db_before[0].prod_id]})
        _, response = cli.delete(url, headers=headers)
        assert 200 == response.status
        list_db_after = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_dict_after = sorted([elem.__dict__['__values__'] for elem in list_db_after], key=itemgetter("prod_id"))
        assert len(list_dict_before) == len(list_dict_after)
        for elem_before, elem_after in zip(list_dict_before, list_dict_after):
            assert elem_before == elem_after


    def test_delete_items_not_int_id(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict],
                 db_user_admin:User, list_db_prod_count_three:list[ProductModel]):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        url = test_app.url_for('products', **{"list_id":["a"]})
        _, response = cli.delete(url, headers=headers)
        assert 400 == response.status

    def test_delete_items_not_exist_id(self, cli: "ReusableClient", test_app: "Sanic", list_dict_prod_count_three:list[dict],
                 db_user_admin:User, list_db_prod_count_three:list[ProductModel]):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        list_db_before = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_dict_before = sorted([elem.__dict__['__values__'] for elem in list_db_before], key=itemgetter("prod_id"))
        max_id = max(elem.prod_id for elem in list_db_before)
        url = test_app.url_for('products', **{"list_id":[max_id+1]})
        _, response = cli.delete(url, headers=headers)
        assert 200 == response.status
        list_db_after = run_corootine_in_current_loop(test_app.config["STORE"].prod_accessor.get_list_of_prod())
        list_dict_after = sorted([elem.__dict__['__values__'] for elem in list_db_after], key=itemgetter("prod_id"))
        assert len(list_dict_before) == len(list_dict_after)
        for elem_before, elem_after in zip(list_dict_before, list_dict_after):
            assert elem_before == elem_after
