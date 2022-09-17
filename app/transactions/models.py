import datetime
from dataclasses import dataclass
from decimal import Decimal

from app.store.database.gino import db


@dataclass
class Transaction:
    transaction_id:int = None
    bill_id:int = None
    amount:Decimal = None
    transaction_date:datetime = None

    def __repr__(self) -> str:
        return f'id:{self.transaction_id}, bill:{self.bill_id}, am:{self.amount}'

class TransactionModel(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, nullable = False, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.bill_id', ondelete="CASCADE"), nullable = False )
    amount = db.Column(db.Numeric(10,2), nullable = False)
    transaction_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
