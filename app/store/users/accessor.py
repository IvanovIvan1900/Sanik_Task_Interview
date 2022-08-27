import typing
from hashlib import sha256
from typing import Optional

from app.store.database.base_accessor import BaseAccessor
from app.users.models import User, UserModel
from app.store.database.gino import db


if typing.TYPE_CHECKING:
    from sanic import Sanic


class UserAccessor(BaseAccessor):
    async def connect(self, sanic_app: "Sanic"):
        await super().connect(sanic_app)
        await self.create_admin(
            login=sanic_app.config["ADMIN_USERNAME"], password=sanic_app.config["ADMIN_PASSWORD"]
        )

    async def get_by_login(self, login: str, is_admin = None) -> Optional[User]:
        query = UserModel.query.where(UserModel.login== login)
        if is_admin is not None:
            query = query.where(UserModel.is_admin == is_admin)
        user = await query.gino.first()
        return User.from_db_model(user) if user is not None else None

    async def create_user(self, user:User)->bool:
        user_db = await UserModel.create(login = user.login, password = User.get_chash_for_password(user.password), 
                is_activate = user.is_activate, is_admin = user.is_admin, key_activete = user.key_activete )
        return user_db

    async def insert_or_find(self, user:User):
        user_db = await self.get_by_login(user.login)
        if user_db is None:
            user_db = await self.create_user(user=user)
            user_db = User.from_db_model(user_db)
        return user_db


    async def create_admin(self, login: str, password: str) -> User:
        admin_in_base = await self.get_by_login(login=login, is_admin=True)
        if admin_in_base is None:
            admin_in_base = await UserModel.create(login = login, password = User.get_chash_for_password(password), 
                is_activate = True, is_admin = True, key_activete = '--------------')
        return User.from_db_model(admin_in_base)