from app.server.server import sanic_app
from app.users.auth import get_jwt_token
from sanic.response import json, text


@sanic_app.get("/users.login/<login:str>/<password:str>", name='users.login')
async def login_user(request, login:str, password:str)->json:
    status_ret = 200
    dict_result = {
        "info": "",
        "token": "",
    }
    user = await sanic_app.config["STORE"].user_accessor.get_by_login(login=login)
    if user is None or not user.is_password_valid(password):
        status_ret = 400
        dict_result["info"] = 'User or login is incorrect'
    else:
        status_ret = 200
        dict_result["token"] = get_jwt_token(user.user_id)

    return json(dict_result, status=status_ret)

