from Crypto.Hash import SHA1
from app.server.server import sanic_app

async def get_signature(transaction_id:int, user_id:int, bill_id:int, amount:int):
    private_key = sanic_app.config["PRIVATE_KEY"]
    hash = SHA1.new()
    hash.update(f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode())
    return hash.hexdigest()
