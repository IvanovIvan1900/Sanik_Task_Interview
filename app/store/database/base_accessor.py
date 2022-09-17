import typing
from logging import getLogger
if typing.TYPE_CHECKING:
    from sanic import Sanic



class BaseAccessor:
    sanic_app: "Sanic" = None
    logger: logger = None
    def __init__(self, sanic_app: "Sanic", *args, **kwargs):
        self.sanic_app = sanic_app
        self.logger = getLogger("accessor")
        sanic_app.register_listener(self.connect, "after_server_start")
        sanic_app.register_listener(self.disconnect, "before_server_stop")

    async def connect(self, sanic_app: "Sanic"):
        return

    async def disconnect(self, sanic_app: "Sanic"):
        return


