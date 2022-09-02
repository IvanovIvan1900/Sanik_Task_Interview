from decimal import Decimal
from typing import Optional
from app.store.database.gino import db
from dataclasses import dataclass

@dataclass
class Transaction:
    trans_id:int = None
    bill_id:int = None
    amount:Decimal = None

    def __repr__(self) -> str:
        return f'id:{self.trans_id}, bill:{self.bill_id}, am:{self.amount}'

class TransactionModel(db.Model):
    __tablename__ = "transactions"

    trans_id = db.Column(db.Integer, nullable = False, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.bill_id', ondelete="CASCADE"), nullable = False )
    amount = db.Column(db.Numeric(10,2), nullable = False)

