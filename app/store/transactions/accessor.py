import typing
from typing import Optional

from app.store.database.base_accessor import BaseAccessor
from app.store.database.gino import db


if typing.TYPE_CHECKING:
    from sanic import Sanic


class TransAccessor(BaseAccessor):
    pass
    # async def get_by_login(self, login: str, is_admin = None) -> Optional[User]:
    #     query = UserModel.query.where(UserModel.login== login)
    #     if is_admin is not None:
    #         query = query.where(UserModel.is_admin == is_admin)
    #     user = await query.gino.first()
    #     return User.from_db_model(user) if user is not None else None

    # async def get_by_id(self, user_id: int) -> Optional[User]:
    #     query = UserModel.query.where(UserModel.user_id == user_id)
    #     user = await query.gino.first()
    #     return User.from_db_model(user) if user is not None else None

    # async def activate_user_wich_key(self, key_activete: str, activate:bool) -> Optional[User]:
    #     user_db = await UserModel.update.values(is_activate=activate).where(UserModel.key_activete == key_activete).returning(*UserModel.__table__.c).gino.first()
    #     return User.from_db_model(user_db) if user_db is not None else None

    # async def get_by_key_activete(self, key_activete: str) -> Optional[User]:
    #     query = UserModel.query.where(UserModel.key_activete == key_activete)
    #     user = await query.gino.first()
    #     return User.from_db_model(user) if user is not None else None

    # async def create_user(self, user:User)->bool:
    #     user_db = await UserModel.create(login = user.login, password = User.get_chash_for_password(user.password), 
    #             is_activate = user.is_activate, is_admin = user.is_admin, key_activete = user.key_activete )
    #     return user_db

    # async def insert_or_find(self, user:User):
    #     user_db = await self.get_by_login(user.login)
    #     if user_db is None:
    #         user_db = await self.create_user(user=user)
    #         user_db = User.from_db_model(user_db)
    #     return user_db


    # async def create_admin(self, login: str, password: str) -> User:
    #     admin_in_base = await self.get_by_login(login=login, is_admin=True)
    #     if admin_in_base is None:
    #         admin_in_base = await UserModel.create(login = login, password = User.get_chash_for_password(password), 
    #             is_activate = True, is_admin = True, key_activete = '--------------')
    #     return User.from_db_model(admin_in_base)