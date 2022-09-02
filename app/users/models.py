from decimal import Decimal
import uuid
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from app.store.database.gino import db

@dataclass
class Bill:
    bill_id:int = None
    summ:Decimal = None
    user_id:int = None

    def __repr__(self) -> str:
        return f'num:{self.bill_id}, summ:{self.summ}, user:{self.user_id}'

@dataclass
class User:
    login: str
    password: Optional[str] = None
    is_activate: bool = None
    is_admin: bool = None
    key_activete: Optional[str] = None
    user_id: Optional[int] = None
    bills: Optional[list["Bill"]] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @staticmethod
    def get_chash_for_password(password:str):
        return sha256(password.encode()).hexdigest()

    @classmethod
    def from_db_model(cls, model) -> Optional["User"]:
        return cls(user_id=model.user_id, login=model.login, password=model.password,
        is_activate = model.is_activate, is_admin = model.is_admin, key_activete = model.key_activete)


class UserModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, nullable = False, primary_key=True)
    login = db.Column(db.String(50), nullable = False, index=True, unique=True)
    password = db.Column(db.String(150))
    is_activate = db.Column(db.Boolean(), nullable = False, default = False)
    is_admin = db.Column(db.Boolean(), nullable = False, default = False)
    key_activete = db.Column(db.String(36),index=True, unique=True, default=uuid.uuid4)


class BillModel(db.Model):
    __tablename__ = "bills"

    bill_id = db.Column(db.Integer, nullable = False, primary_key=True)
    summ = db.Column(db.Numeric(10,2), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"))

    _c = db.CheckConstraint('summ >= 0', name='summ_not_negative')
