import typing
from wsgiref import headers

import pytest
from app.users.auth import get_jwt_token
from app.users.models import User
from sanic import Sanic, response
from tests.fixtures.users import (create_user_from_dict,
                                  get_header_auth_wich_user)

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
        headers = get_header_auth_wich_user(dict_user_data.get("user_id", None))
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