from sanic import Sanic
import logging

def setup_logging(sanic_app: Sanic) -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('').setLevel(logging.DEBUG)
    _log_format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_log_format))
    logging.getLogger('').addHandler(console)
    ch_info = logging.FileHandler('log_info.log')
    ch_info.setLevel(logging.INFO)
    ch_info.setFormatter(logging.Formatter(_log_format))
    logging.getLogger('').addHandler(ch_info)
    ch_debug = logging.FileHandler('log_debug.log')
    ch_debug.setLevel(logging.DEBUG)
    ch_debug.setFormatter(logging.Formatter(_log_format))
    logging.getLogger('').addHandler(ch_debug)
    sanic_app.config["LOGGER"] = logging.getLogger('')