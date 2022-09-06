from sanic import Sanic

def setup_config(sanic_app: Sanic)->None:
    sanic_app.config["ADMIN_USERNAME"] = 'admin'
    sanic_app.config["ADMIN_PASSWORD"] = 'password'
    sanic_app.config["SECRET_KEY"] = 'cef3904660bd'
    sanic_app.config["PRIVATE_KEY"] = 'cef3904660bd'

