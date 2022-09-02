from typing import Optional

from sanic import Sanic
from sanic.response import text
from app.server.config import setup_config
from app.store import setup_store
from app.server.logging import setup_logging
from sanic_openapi import openapi3_blueprint


sanic_app = Sanic.get_app("Magazin_API", force_create=True)

def setup_app(sanic_app:Sanic)->None:
    setup_logging(sanic_app)
    setup_config(sanic_app)
    setup_store(sanic_app)

if __name__ == "__main__":
    setup_app(sanic_app)
    sanic_app.blueprint(openapi3_blueprint)
    sanic_app.run(host='127.0.0.1', port=5566, debug=True, access_log=True, )