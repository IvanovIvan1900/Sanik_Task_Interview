import json
import uuid
from app.transactions.schemes import ListBillsInput, ListBillsOutput
from app.users.models import User
from sanic.response import json as json_resp

from app.server.server import sanic_app
from app.users.auth import (authorized, get_jwt_token, get_link_activate_user,
                            is_admin)
from app.users.schemes import (LoginInput, LoginResponse,
                               RegisterNewUserResponse,
                               UsersActivateRequest, UsersId_AndActive, UsersInfoResponse)
from sanic_openapi import openapi
from sanic_openapi.openapi3.definitions import RequestBody, Response
from sanic_pydantic import webargs
from sqlalchemy.exc import IntegrityError
from sanic.request import Request
from app.transactions.utils import DecimalEncoder


@sanic_app.get("/users.login/", name='users.login')
@openapi.description('Login to api and get token')
@openapi.definition(
    body=RequestBody(LoginInput, required=True),
    response=[Response(LoginResponse)],
)
@webargs(query=LoginInput)
async def user_login(request:Request, **kwargs)->json_resp:
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

    return json_resp(dict_result, status=status_ret)


@sanic_app.get("/users.register.new/", name='users.register.new')
@openapi.description('Register new user')
@openapi.definition(
    body=RequestBody(LoginInput, required=True),
    response=[Response(RegisterNewUserResponse)],
)
@webargs(query=LoginInput)
async def user_register(request:Request, **kwargs)->json_resp:
    status_ret = 200
    dict_result = {
        "info": "",
        "link_to_activate": "",
        "user_id":""
    }
    login = kwargs['query']['login']
    password = kwargs['query']['password']
    user_db = await sanic_app.config["STORE"].user_accessor.get_by_login(login=login)
    if user_db is not None:
        status_ret = 400
        dict_result["info"] = f'User wich login {login} already exists'
        return json_resp(dict_result, status=status_ret)
    dict_new_user = {
        "login":login,
        "password":password,
        "is_activate": False,
        "is_admin": False,
        "key_activete":str(uuid.uuid4()),
    }
    count = 5
    while count > 0:
        try:
            user_db = await sanic_app.config["STORE"].user_accessor.create_user(User(**dict_new_user))
            break
        except IntegrityError as e:
            sanic_app.config["LOGGER"].debug(f'User wich key activationa "{dict_new_user["key_activete"]}" is already exists')
            dict_new_user["key_activete"] = str(uuid.uuid4())
            user_db = None
        except Exception as e:
            user_db = None
            sanic_app.config["LOGGER"].error(f'Error create new user. Exception is "{e}"')
            status_ret = 400
            dict_result["info"] = f'Exceptin is "{e}"'
            break

        count -= 1

    if user_db is not None:
        dict_result["link_to_activate"] = get_link_activate_user(user_db)
        dict_result["info"] = "User create but inactive"
        dict_result["user_id"] = user_db.user_id

    return json_resp(dict_result, status=status_ret)


@sanic_app.get("/users.activate/", name='users.activate')
@openapi.description('Activete inactive user')
@openapi.definition(
    body=RequestBody(UsersActivateRequest, required=True),
    response=[Response(UsersInfoResponse)],
)
@webargs(query=UsersActivateRequest)
async def user_activate(request:Request, **kwargs)->json_resp:
    status_ret = 200
    dict_result = {
        "info": "",
    }
    key = kwargs['query']['key']
    user_db = await sanic_app.config["STORE"].user_accessor.get_by_key_activete(key_activete=key)
    if user_db is None:
        status_ret = 400
        dict_result["info"] = f'Key "{key}" is not found'
        return json_resp(dict_result, status=status_ret)
    if user_db.is_activate:
        status_ret = 400
        dict_result["info"] = f'Users wich key "{key}" already is activate'
        return json_resp(dict_result, status=status_ret)

    user = await sanic_app.config["STORE"].user_accessor.activate_user_wich_key(key_activete=key, activate = True)
    if user:
        dict_result["info"] = f'Users activte'
        return json_resp(dict_result, status=status_ret)
    else:
        status_ret = 400
        dict_result["info"] = f'Uncnown error. see logs'
        return json_resp(dict_result, status=status_ret)

@sanic_app.get("/users.set_is_active/", name='users.set_is_active')
@openapi.description('Activete inactive user')
@openapi.definition(
    body=RequestBody(UsersId_AndActive, required=True),
    response=[Response(UsersInfoResponse)],
)
@authorized
@is_admin
@webargs(query=UsersId_AndActive)
async def user_activate(request:Request, **kwargs)->json_resp:
    status_ret = 200
    dict_result = {
        "info": "",
    }
    user_id = kwargs["query"]["user_id"]
    is_active = kwargs["query"]["is_active"]
    user = await sanic_app.config["STORE"].user_accessor.get_by_id(user_id)
    if user is None:
        dict_result["info"] = f'Error. User wich user_id {user_id} is not exists'
        status_ret = 400
    else:
        if user.is_activate != is_active:
            user = await sanic_app.config["STORE"].user_accessor.activate_user_id(user_id, is_active)
            dict_result["info"] = "ok"
    return json_resp(dict_result, status=status_ret)

@sanic_app.get("/users.test.auth/", name='users.test.auth')
@authorized
async def test_auth(request:Request, **kwargs)->json_resp:
    return json_resp({'info':'user is auth'}, status=200)

@sanic_app.get("/users.test.auth.admin/", name='users.test.auth.admin')
@authorized
@is_admin
async def test_auth(request:Request, **kwargs)->json_resp:
    return json_resp({'info':'user is admin'}, status=200)


@sanic_app.get("/users/get_bills", name='users.get.bills')
@openapi.description('Get users and bills')
@openapi.definition(
    body=RequestBody(ListBillsInput, required=False),
    response=[Response(ListBillsOutput)],
)
@authorized
@is_admin
@webargs(query=ListBillsInput)
async def transaction_buy(request:Request, **kwargs) -> json_resp:
    status_ret = 200
    dic_queyr_filter = {key:kwargs["query"].get(key) for key in ["user_id", "bill_id"] if kwargs["query"].get(key, None) is not None}
    result = await sanic_app.config["STORE"].user_accessor.get_user_wich_bills(**dic_queyr_filter)
    items = []
    for elem in result:
        dic_data = {"user_id":elem.user_id, "login":elem.login,"bills":[]}
        for bill in elem.bills:
            dic_data["bills"].append({"bill_id":bill.bill_id, "amount":bill.amount})
        items.append(dic_data)
    dict_result = {"info": "", "items": items}
    json_str = json.dumps(dict_result, cls=DecimalEncoder)
    return json_resp(json_str, status= status_ret)
