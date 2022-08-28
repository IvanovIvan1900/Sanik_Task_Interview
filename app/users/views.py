from app.server.server import sanic_app
from app.users.auth import authorized, get_jwt_token, is_admin
from app.users.schemes import LoginInput, LoginResponse
from sanic.response import json, text
from sanic_openapi import openapi
from sanic_openapi.openapi3.definitions import RequestBody, Response
from sanic_pydantic import webargs


@sanic_app.get("/users.login/", name='users.login')
@openapi.description('Login to api and get token')
@openapi.definition(
    body=RequestBody(LoginInput, required=True),
    summary="User profile update",
    response=[Response(LoginResponse)],
)
@webargs(query=LoginInput)
async def login_user(request, **kwargs)->json:
    status_ret = 200
    dict_result = {
        "info": "",
        "token": "",
    }
    login = kwargs['query']['login']
    password = kwargs['query']['password']
    user = await sanic_app.config["STORE"].user_accessor.get_by_login(login=login)
    if user is None or not user.is_password_valid(password):
        status_ret = 400
        dict_result["info"] = 'User or login is incorrect'
    else:
        status_ret = 200
        dict_result["token"] = get_jwt_token(user.user_id)

    return json(dict_result, status=status_ret)


@sanic_app.get("/users.test.auth/", name='users.test.auth')
@authorized
async def test_auth(request, **kwargs)->json:
    return json({'info':'user is auth'}, status=200)

@sanic_app.get("/users.test.auth.admin/", name='users.test.auth.admin')
@authorized
@is_admin
async def test_auth(request, **kwargs)->json:
    return json({'info':'user is admin'}, status=200)