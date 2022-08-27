import typing
from wsgiref import headers
import pytest
from sanic import Sanic, response
from app.users.auth import get_jwt_token
from app.users.models import User

if typing.TYPE_CHECKING:
    from sanic import Sanic
    from sanic_testing.reusable import ReusableClient

class TestUsers:

    def test_login_incorrect_login(self, cli: "ReusableClient", test_app: "Sanic"):
        url = test_app.url_for('users.login', login='test_login', password='test_password')
        # request, response = await test_app.asgi_client.get(url, headers = {"Authorization": "Bearer MYREALLYLONGTOKENIGOT"})
        request, response = cli.get(url)
        # request, response = app.test_client.get("/")

        # assert request.method.lower() == "get"
        # assert response.body == b"foo"
        assert response.status == 400
        print("end test 1")
        test_app.router.reset()


    def test_login_correct_login(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, dict_user_admin:dict):
        url = test_app.url_for('users.login', login=db_user_admin.login, password=dict_user_admin.get("password"))
        request, response = cli.get(url)
        assert response.status == 200

        token = get_jwt_token(db_user_admin.user_id)

        assert token == response.json['token']

# class TestTest:
#     def test_1(self, cli: "ReusableClient", test_app: "Sanic"):
#         url = test_app.url_for('users.login', login='test_login', password='test_password')
#         request, response = cli.get(url)
#         assert response.status == 400

#     def test_wich_db_data(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User):
#         url = test_app.url_for('users.login', login=db_user_admin.login, password=db_user_admin.password)
#         request, response = cli.get(url)
#         assert response.status == 200

