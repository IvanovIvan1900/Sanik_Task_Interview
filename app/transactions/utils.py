import datetime
from decimal import Decimal
from json import JSONEncoder

from app.server.server import sanic_app
from Crypto.Hash import SHA1


async def get_signature(transaction_id:int, user_id:int, bill_id:int, amount:int):
    private_key = sanic_app.config["PRIVATE_KEY"]
    hash = SHA1.new()
    hash.update(f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode())
    return hash.hexdigest()

# т.к. нам необходимо исползовать 2 encodera, для даты и decimal, слямзим этот класс
# https://stackoverflow.com/questions/65338261/combine-multiple-json-encoders
class MultipleJsonEncoders():
    """
    Combine multiple JSON encoders
    """
    def __init__(self, *encoders):
        self.encoders = encoders
        self.args = ()
        self.kwargs = {}

    def default(self, obj):
        for encoder in self.encoders:
            try:
                return encoder(*self.args, **self.kwargs).default(obj)
            except TypeError:
                pass
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        enc = JSONEncoder(*args, **kwargs)
        enc.default = self.default
        return enc

class DateTimeEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return super().default(obj)

class DecimalEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
