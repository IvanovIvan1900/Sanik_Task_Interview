import hmac
from typing import Optional
from app.server.server import sanic_app
import pickle
from  hashlib import sha256
import base64
from functools import wraps
from sanic.response import json

def base64urlEncode_dict(input_data:dict)->str:
    return base64.b64encode(pickle.dumps(input_data))

def base64urlDecode_dict(input_data_b64:str)->dict:
    return pickle.loads(base64.b64decode(input_data_b64.encode('utf-8')))

def get_jwt_token(user_id: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"user_id": str(user_id)}
    secret_key = sanic_app.config["SECRET_KEY"]
    unsignedToken = base64urlEncode_dict(header)+b'.'+base64urlEncode_dict(payload)
    signature = hmac.new(secret_key.encode('utf-8'), unsignedToken, sha256).hexdigest()
    unsignedToken_str = unsignedToken.decode('utf-8')
    return f'{unsignedToken_str}.{signature}'

def check_is_signature(token:str)->bool:
    correct = False
    if token:
        try:
            token_part = token.split('.')
            unsignedToken = f'{token_part[0]}.{token_part[1]}'
            secret_key = sanic_app.config["SECRET_KEY"]
            signature = token_part[2]
            signature_correct = hmac.new(secret_key.encode('utf-8'), unsignedToken.encode('utf-8'), sha256).hexdigest()
            correct = signature_correct == signature
        except Exception as e:
            sanic_app.config["LOGGER"].error(f'Exception in check token. Token is "{token}". Exception is "{e}"')

    return correct

def get_user_id_from_token(token:str)->Optional[str]:
    user_id = None
    if token:
        try:
            token_part = token.split('.')
            pay_load = base64urlDecode_dict(token_part[1])
            if isinstance(pay_load, dict):
                user_id = pay_load.get("user_id", None)
        except Exception as e:
            sanic_app.config["LOGGER"].error(f'Exception in get user_id from token. Token is "{token}". Exception is "{e}"')

    return user_id

def get_tocken_from_header_value(header_value: str)->str:
    token = ''
    prefix = 'Basic'
    if header_value.startswith(prefix):
        token = header_value[len(prefix):].strip()
    return token

@sanic_app.middleware("request")
async def extract_user(request):
    user = None
    if request.token is not None:
        token = get_tocken_from_header_value(request.token)
        if not check_is_signature(token):
            return json({"info": "Token is not correct"}, status=400)
        user_id = get_user_id_from_token(token)
        try:
            user_id = int(user_id)
        except ValueError as e:
            sanic_app.config["LOGGER"].error(f'Error convert user id from token to int. User_id is {user_id}')

            user_id = None
        if user_id is None:
            return json({"info": "User_id from token is not int"}, status=400)
        user = await sanic_app.config["STORE"].user_accessor.get_by_id(user_id=user_id)
        if user is not None and not user.is_activate:
            return json({"info": f"User wich user_id {user_id} is not activated yet"}, status=400)

    request.ctx.user = user

def authorized(wrapped):
    def actual_decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            if request.ctx.user is None:
                return json({"info":"User is not definded"}, status = 401)
            # elif is_admin and not request.ctx.user.is_admin:
            #     return json({"info":"User {request.ctx.user.login} wich user_id {request.ctx.user.user_id} is not admin"}, status = 403)
            response = await func(request, *args, **kwargs)
            return response
        return decorated_function
    return actual_decorator(wrapped)

def is_admin(wrapped):
    def actual_decorator(func):
        @wraps(func)
        async def decorated_function(request, *args, **kwargs):
            if request.ctx.user is not None and  not request.ctx.user.is_admin:
                 return json({"info":f"User {request.ctx.user.login} wich user_id {request.ctx.user.user_id} is not admin"}, status = 403)
            response = await func(request, *args, **kwargs)
            return response
        return decorated_function
    return actual_decorator(wrapped)