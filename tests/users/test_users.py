import typing
from wsgiref import headers
import pytest
from sanic import Sanic, response
from tests.fixtures.users import create_user_from_dict
from app.users.auth import get_jwt_token
from app.users.models import User

if typing.TYPE_CHECKING:
    from sanic import Sanic
    from sanic_testing.reusable import ReusableClient

class TestUsers:
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
