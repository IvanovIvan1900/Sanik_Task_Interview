import json
import typing
import uuid
from wsgiref import headers

import pytest
from app.users.auth import get_jwt_token
from app.users.models import Bill, User
from pytest_dictsdiff import check_objects
from sanic import Sanic, response
from tests.fixtures.general import run_corootine_in_current_loop
from tests.fixtures.users import (create_user_from_dict,
                                  get_header_auth_wich_user)
from tests.transactions.test_transaction import TestTransactions

if typing.TYPE_CHECKING:
    from sanic import Sanic
    from sanic_testing.reusable import ReusableClient

class TestUsersLogin:
    @pytest.mark.parametrize("dict_user_data, create_user, status",
        [
            (pytest.lazy_fixture("dict_user_admin"),True,200),
            (pytest.lazy_fixture("dict_user_admin"),False,400),
            (pytest.lazy_fixture("dict_user_empty_pass"),True,200),
            ({"login":"test login"},False,400),
            ({},False,422),
        ]
    )
    def test_login_input_param(self, cli: "ReusableClient", test_app: "Sanic", dict_user_data:dict, create_user:bool, status:int):
        param_url = {}
        user_db = None
        if "login" in dict_user_data:
            param_url["login"] = dict_user_data["login"]
        if "password" in dict_user_data:
            param_url["password"] = dict_user_data["password"]
        if create_user:
            user_db = create_user_from_dict(test_app=test_app, dict_user_data=dict_user_data)
        url = test_app.url_for('users.login', **param_url)
        _, response = cli.get(url)
        assert response.status == status
        if status == 200 and user_db is not None:
            token = get_jwt_token(user_db.user_id)
            assert token == response.json['token']

    def test_correct_login_and_incorrect_pass(self, cli: "ReusableClient", test_app: "Sanic", dict_user_1_activate:dict,):
        user_db = create_user_from_dict(test_app=test_app, dict_user_data=dict_user_1_activate)
        dict_user_1_activate["password"] = "incorrect pass"
        self.test_login_input_param(cli, test_app, dict_user_data=dict_user_1_activate, create_user=False, status=400)

    def test_type_of_request(self, cli: "ReusableClient", test_app: "Sanic"):
        _, response = cli.post('users.login')
        assert response.status == 405
        assert response.headers["allow"] == 'GET'

    @pytest.mark.parametrize("dict_user_data, create_user, status, info",
        [
            (pytest.lazy_fixture("dict_user_admin"),True,200, "user is auth"),
            (pytest.lazy_fixture("dict_user_1_activate"),True,200, "user is auth"),
            (pytest.lazy_fixture("dict_user_2_non_activate"),True,400, "User wich user_id {user_id} is not activated yet"),
            ({"login":"test login", "user_id":"80a"},False,400, "User_id from token is not int"),
            ({"login":"test login", "user_id":"10000000"},False,401, "User is not definded"),
        ]
    )
    def test_authorization(self, cli: "ReusableClient", test_app: "Sanic", dict_user_data:dict, 
            create_user:bool, status:int, info:typing.Optional[str]):
        user_db = None
        if create_user:
            user_db = create_user_from_dict(test_app=test_app, dict_user_data=dict_user_data)
            dict_user_data["user_id"] = user_db.user_id
        # headers = get_header_auth_wich_user(dict_user_data.get("user_id", None))
        token = get_jwt_token(dict_user_data.get("user_id", None))
        headers = {'Authorization':f'Basic {token}'}

        request, response = cli.get('users.test.auth', headers=headers)

        assert status == response.status

        if info:
            if dict_user_data.get('user_id', None):
                info = info.replace("{user_id}", str(dict_user_data.get('user_id', None)))
            if dict_user_data.get('user_id', None):
                info = info.replace("{user_login}", dict_user_data.get('login', None))

            assert info == response.json["info"]

    def test_authorization_not_correct_token(self, cli: "ReusableClient", test_app: "Sanic"):
        token1 = get_jwt_token(80)
        token2 = get_jwt_token(100)
        token_not_correct = f'{token1.split(".")[0]}.{token1.split(".")[1]}.{token2.split(".")[2]}'
        headers = {'Authorization':f'Basic {token_not_correct}'}
        request, response = cli.get('users.test.auth', headers=headers)

        assert 400 == response.status

        assert "Token is not correct" == response.json["info"]

    def test_authorization_not_valid_token(self, cli: "ReusableClient", test_app: "Sanic"):
        token = f"AAA{get_jwt_token(80)[3:]}"
        headers = {'Authorization': f'Basic {token}'}
        request, response = cli.get('users.test.auth', headers=headers)
        assert 400 == response.status
        assert "Token is not correct" == response.json["info"]

    @pytest.mark.parametrize("dict_user_data, create_user, status, info",
        [
            (pytest.lazy_fixture("dict_user_admin"),True,200, "user is admin"),
            (pytest.lazy_fixture("dict_user_1_activate"),True,403, "User {user_login} wich user_id {user_id} is not admin"),
        ]
    )
    def test_authorization_is_admin(self, cli: "ReusableClient", test_app: "Sanic", dict_user_data:dict, 
            create_user:bool, status:int, info:typing.Optional[str]):
        user_db = None
        if create_user:
            user_db = create_user_from_dict(test_app=test_app, dict_user_data=dict_user_data)
            dict_user_data["user_id"] = user_db.user_id
        headers = get_header_auth_wich_user(dict_user_data.get("user_id", None))
        request, response = cli.get('users.test.auth.admin', headers=headers)

        assert status == response.status

        if info:
            if dict_user_data.get('user_id', None):
                info = info.replace("{user_id}", str(dict_user_data.get('user_id', None)))
            if dict_user_data.get('user_id', None):
                info = info.replace("{user_login}", dict_user_data.get('login', None))

            assert info == response.json["info"]

class TestUsersCreateAndActivate:

    def test_create_user_and_activate(self, cli: "ReusableClient", test_app: "Sanic"):
        param_url = {
            "login":"test_login",
            "password":"test_password"
        }
        url = test_app.url_for('users.register.new', **param_url)
        _, response = cli.get(url)

        assert 200 == response.status
        user_id = int(response.json["user_id"])
        user_db = run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.get_by_id(user_id = user_id))

        assert user_db
        assert not user_db.is_activate

        _, response = cli.get(response.json["link_to_activate"])

        assert 200 == response.status

        user_db = run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.get_by_id(user_id = user_id))

        assert user_db
        assert user_db.is_activate

    def test_create_user_already_exists(self, cli: "ReusableClient", test_app: "Sanic", db_user_1_activate:User):
        param_url = {
            "login":db_user_1_activate.login,
            "password":db_user_1_activate.password
        }
        url = test_app.url_for('users.register.new', **param_url)
        _, response = cli.get(url)

        assert 400 == response.status
        assert f'User wich login {db_user_1_activate.login} already exists' == response.json["info"]

    def test_activate_wich_invalide_key(self, cli: "ReusableClient", test_app: "Sanic"):
        key=str(uuid.uuid4())
        url = test_app.url_for('users.activate', key=key)
        _, response = cli.get(url)

        assert 400 == response.status
        assert f'Key "{key}" is not found' == response.json["info"]

    def test_activate_already_active_user(self, cli: "ReusableClient", test_app: "Sanic", db_user_1_activate:User):
        url = test_app.url_for('users.activate', key=db_user_1_activate.key_activete)
        _, response = cli.get(url)

        assert 400 == response.status
        assert f'Users wich key "{db_user_1_activate.key_activete}" already is activate' == response.json["info"]

    def test_activate_user_by_id_not_exist(self, cli: "ReusableClient", test_app: "Sanic", db_user_1_activate:User, db_user_admin:User,):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        user_id = db_user_admin.user_id+1
        url = test_app.url_for('users.set_is_active', user_id=user_id, is_active=True)
        _, response = cli.get(url, headers = headers)

        assert 400 == response.status
        assert f'Error. User wich user_id {user_id} is not exists' == response.json["info"]

    def test_activate_user_by_id(self, cli: "ReusableClient", test_app: "Sanic", db_user_1_activate:User,
                 db_user_admin:User):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        user_id = db_user_1_activate.user_id
        url = test_app.url_for('users.set_is_active', user_id=user_id, is_active=False)
        _, response = cli.get(url, headers = headers)

        assert 200 == response.status
        user_db = run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.get_by_id(user_id))
        assert user_db is not None
        assert not user_db.is_activate

        url = test_app.url_for('users.set_is_active', user_id=user_id, is_active=True)
        _, response = cli.get(url, headers = headers)

        assert 200 == response.status
        user_db = run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.get_by_id(user_id))
        assert user_db is not None
        assert user_db.is_activate

class TestListBill():
    
    def service_get_list_bills(self, list_transaction:list[dict], list_bill:list[dict], filters:dict
            , list_of_user:User)->list[dict]:
        dict_bill_id_to_user_id = {elem["bill_id"]:elem["user_id"] for elem in list_bill}
        dict_user_id_to_login = {elem.user_id:elem.login for elem in list_of_user}
        set_of_bills = None
        dict_result = {}
        if filters.get("user_id", None) is not None or filters.get("bill_id", None) is not None:
            set_of_bills = set()
            if filters.get("user_id", None) is not None:
                set_of_bill_for_user_id = {elem["bill_id"] for elem in list_bill if elem["user_id"] == filters["user_id"]}
            else:
                set_of_bill_for_user_id = {elem["bill_id"] for elem in list_bill}
            if filters.get("bill_id", None) is not None:
                set_of_bills_for_bills_id = {elem["bill_id"] for elem in list_bill if elem["bill_id"] == filters["bill_id"]}
            else:
                set_of_bills_for_bills_id = {elem["bill_id"] for elem in list_bill}
            set_of_bills = set_of_bill_for_user_id.intersection(set_of_bills_for_bills_id)

        for elem in list_transaction:
            if set_of_bills is not None and elem["bill_id"] not in set_of_bills:
                continue
            user_id = dict_bill_id_to_user_id.get(elem["bill_id"], None)
            user_dict = dict_result.get(user_id)
            if user_dict is None:
                dict_result[user_id] = {"bills":{}, "login":dict_user_id_to_login.get(user_id, "")}
            bills = dict_result.get(user_id)["bills"]
            if bills.get(elem["bill_id"]) is None:
                bills[elem["bill_id"]] = {"amount": 0}
            bills[elem["bill_id"]]["amount"] = bills[elem["bill_id"]]["amount"] + elem["amount"]

            # elem_add = elem.copy()
            # elem_add["user_id"] =
            # elem_add["login"] = dict_user_id_to_login.get(elem_add["user_id"], None)
            # elem_add["transaction_date"] = elem_add["transaction_date"].isoformat()
            # elem_add["transaction_id"] = ANY
            # elem_add["amount"] = str(elem_add["amount"])
            # list_of_result.append(elem_add)
        result_list = []
        for key, value in dict_result.items():
            dict_data = {"user_id":key, "login":value["login"], "bills":[]}
            for k, v in value["bills"].items():
                dic_value = dict(**{"bill_id":k}, **v )
                dic_value["amount"] = str(dic_value["amount"])
                dict_data["bills"].append(dic_value)
            result_list.append(dict_data)
        return result_list


    @pytest.mark.parametrize("user, bill",
            [
                (None,None),
                (pytest.lazy_fixture("db_user_admin"), None),
                (pytest.lazy_fixture("db_user_admin"), pytest.lazy_fixture("dict_bill_one")),
                (None, pytest.lazy_fixture("dict_bill_one")),
                # (pytest.lazy_fixture(""), pytest.lazy_fixture("")),
                # (pytest.lazy_fixture(""), pytest.lazy_fixture("")),
                # (pytest.lazy_fixture(""), pytest.lazy_fixture("")),
            ]
        )

    def test_bill_list(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, db_user_1_activate:User, dict_bill_one:dict,
            dict_bill_two:dict, dict_bill_three:dict, list_dict_transactions_10:list[dict],
            user:User, bill:Bill):
        class_test = TestTransactions()
        class_test.service_list_transaction_create_data(cli, test_app, db_user_admin, db_user_1_activate, dict_bill_one, dict_bill_two, 
                    dict_bill_three, list_dict_transactions_10)
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        data_query = {}
        if user is not None:
            data_query["user_id"] = user.user_id
        if bill is not None:
            data_query["bill_id"] = bill["bill_id"]

        url = test_app.url_for('users.get.bills', **data_query)
        _, response = cli.get(url, headers=headers)

        assert 200 == response.status
        json_data = json.loads(response.json)
        etalon_date = self.service_get_list_bills(list_transaction=list_dict_transactions_10, list_bill=[dict_bill_one, dict_bill_two, dict_bill_three], 
                    filters=data_query, list_of_user=[db_user_admin, db_user_1_activate])
        assert len(etalon_date) == len(json_data["items"])
        key_func = lambda x: (x["user_id"])
        key_bills = lambda x: x["bill_id"]
        for elem_etalon, elem_db in zip(sorted(etalon_date, key=key_func), sorted(json_data["items"], key=key_func)):
            assert elem_etalon["user_id"] == elem_db["user_id"]
            assert elem_etalon["login"] == elem_db["login"]
            assert check_objects(sorted(elem_etalon["bills"], key=key_bills), sorted(elem_db["bills"], key=key_bills), verbose=1)

