from typing import Optional

from app.store.database.gino import db
from app.users.models import *
from sanic import Sanic
from sqlalchemy.engine.url import URL

import gino
from gino.api import Gino


class Database():
    db: Gino
    is_connect:bool
    app:Sanic

    def __init__(self, app: Sanic):
        self.app = app
        self.db: Optional[Gino] = None
        self.is_connect = False

    async def connect(self, *_, **kw):
        if not self.is_connect:
            try:
                self._engine = await gino.create_engine(
                    URL(
                        drivername="asyncpg",
                        host=self.app.config["DB_HOST"],
                        database=self.app.config["DB_NAME"],
                        username=self.app.config["DB_USER"],
                        password=self.app.config["DB_PASSWORD"],
                        port=self.app.config["DB_PORT"],
                    ),
                    min_size=1,
                    max_size=1,
                )
                self.db = db
                self.db.bind = self._engine
                self.is_connect = True
            except Exception as e:
                self.app.config["LOGGER"].error(f'Error connect database. Exception is {e}')
            else:
                self.app.config["LOGGER"].debug('Connect db is succesfully')

    async def disconnect(self, *_, **kw):
        if self.is_connect:
            self.engine, self.db.bind = self.db.bind, None
            await self.engine.close()
            self.app.config["LOGGER"].debug('Stop connection db is succesfully')
            self.is_connect = False
        else:
            self.app.config["LOGGER"].error('Error stop connection db. Server is not started')

    async def clear_db(self):
        db = self.db
        for table in db.sorted_tables:
            await db.status(db.text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE"))
