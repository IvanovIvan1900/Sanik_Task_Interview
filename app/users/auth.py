import hmac
from typing import Optional
from app.server.server import sanic_app
import pickle
from  hashlib import sha256
import base64

def base64urlEncode_dict(input_data:dict)->str:
    return base64.b64encode(pickle.dumps(input_data))

def base64urlDecode_dict(input_data_b64:str)->dict:
    return pickle.loads(input_data_b64.decode('base64', 'strict'))

def get_jwt_token(user_id: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"userId": str(user_id)}
    secret_key = sanic_app.config["SECRET_KEY"]
    unsignedToken = base64urlEncode_dict(header)+b'.'+base64urlEncode_dict(payload)
    signature = hmac.new(secret_key.encode('utf-8'), unsignedToken, sha256).hexdigest()
    return f'{unsignedToken}.{signature}'

def check_is_signature(token:str)->bool:
    correct = False
    if token:
        token_part = token.split('.')
        unsignedToken = f'{token_part[0]}.{token_part[1]}'
        secret_key = sanic_app.config["SECRET_KEY"]
        signature = token_part[2]
        signature_correct = hmac.new(secret_key.encode('utf-8'), unsignedToken, sha256).hexdigest()

        correct = signature_correct == signature

    return correct

def get_user_id_from_token(token:str)->Optional[str]:
    user_id = None
    if token:
        token_part = token.split('.')
        pay_load = base64urlDecode_dict(token_part[1])
        if isinstance(pay_load, dict):
            user_id = pay_load.get("user_id", None)

    return user_id