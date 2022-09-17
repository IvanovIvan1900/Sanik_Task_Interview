import typing

from app.store.database.database import Database
from app.store.products.accessor import ProdAccessor
from app.store.transactions.accessor import TransAccessor

if typing.TYPE_CHECKING:
    from sanic import Sanic


class Store:
    def __init__(self, sanic_app: "Sanic"):
        from app.store.users.accessor import UserAccessor
        self.user_accessor:UserAccessor = UserAccessor(sanic_app)
        self.prod_accessor:ProdAccessor = ProdAccessor(sanic_app)
        self.trans_accessor:TransAccessor = TransAccessor(sanic_app)

async def connect_db(sanic_app: "Sanic"):
    await sanic_app.config["DATABASE"].connect()

async def close_connect_db(sanic_app: "Sanic"):
    await sanic_app.config["DATABASE"].disconnect()

def setup_store(sanic_app: "Sanic")->None:
    sanic_app.config["DB_HOST"] = '127.0.0.1'
    sanic_app.config["DB_PORT"] = '5454'
    sanic_app.config["DB_USER"] = 'sanic_test'
    sanic_app.config["DB_PASSWORD"] = 'pgpwd4habr'
    sanic_app.config["DB_NAME"] = 'sanic_test'

    sanic_app.config["DATABASE"] = Database(sanic_app)
    sanic_app.register_listener(connect_db, "before_server_start")
    sanic_app.register_listener(close_connect_db, "before_server_stop")

    sanic_app.config["STORE"]:Store = Store(sanic_app)
