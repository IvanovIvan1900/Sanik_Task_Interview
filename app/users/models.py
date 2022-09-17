from decimal import Decimal
import uuid
from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from app.store.database.gino import db

@dataclass
class Bill:
    bill_id:int = None
    amount:Decimal = None
    user_id:int = None

    def __repr__(self) -> str:
        return f'num:{self.bill_id}, amount:{self.amount}, user:{self.user_id}'

    @classmethod
    def from_db_model(cls, model) -> Optional["Bill"]:
        return cls(bill_id=model.bill_id, amount=model.amount, user_id=model.user_id)

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

    def __repr__(self) -> str:
        return f'login: {self.login}, user_id: {self.user_id}'

    def __init__(self, **kw):
            super().__init__(**kw)
            self._bills = set()
    @property
    def bills(self):
        return self._bills

    @bills.setter
    def add_bill(self, bill):
        self._bills.add(bill)


class BillModel(db.Model):
    __tablename__ = "bills"

    bill_id = db.Column(db.Integer, nullable = False, primary_key=True)
    amount = db.Column(db.Numeric(10,2), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"))

    _c = db.CheckConstraint('amount >= 0', name='amount_not_negative')

    def __repr__(self) -> str:
        return f'user_id:{self.user_id}, bill_id:{self.bill_id}, amount:{self.amount}'