from dataclasses import dataclass
from hashlib import sha256
from typing import Optional
import uuid

from app.store.database.gino import db

@dataclass
class User:
    login: str
    password: Optional[str] = None
    is_activate: bool = None
    is_admin: bool = None
    key_activete: Optional[str] = None
    user_id: Optional[int] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @staticmethod
    def get_chash_for_password(password:str):
        return sha256(password.encode()).hexdigest()

    # @classmethod
    # def from_dict(cls, dict_data:dict)->Optional["User"]:
    #     cls(**dict_data)

    @classmethod
    def from_db_model(cls, model) -> Optional["User"]:
        return cls(user_id=model.user_id, login=model.login, password=model.password,
        is_activate = model.is_activate, is_admin = model.is_admin, key_activete = model.key_activete)

# TODO
# Дописать все необходимые поля модели
class UserModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, nullable = False, primary_key=True)
    login = db.Column(db.String(50), nullable = False, index=True, unique=True)
    password = db.Column(db.String(150))
    is_activate = db.Column(db.Boolean(), nullable = False, default = False)
    is_admin = db.Column(db.Boolean(), nullable = False, default = False)
    key_activete = db.Column(db.String(36),index=True, unique=True, default=uuid.uuid4)