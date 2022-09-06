from decimal import Decimal
from operator import index
from typing import Optional
from app.store.database.gino import db
from dataclasses import dataclass

@dataclass
class Transaction:
    transaction_id:int = None
    bill_id:int = None
    amount:Decimal = None

    def __repr__(self) -> str:
        return f'id:{self.transaction_id}, bill:{self.bill_id}, am:{self.amount}, us:{self.user_id}'

class TransactionModel(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, nullable = False, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.bill_id', ondelete="CASCADE"), nullable = False )
    amount = db.Column(db.Numeric(10,2), nullable = False)
