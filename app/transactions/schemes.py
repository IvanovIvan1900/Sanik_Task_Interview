from ast import List
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class PaymentInputs(BaseModel):
    signature:str
    transaction_id:int
    user_id:int
    bill_id:int
    amount:int

class PaymentOuput(BaseModel):
    info:str

class BayProd(BaseModel):
    prod_id:int
    count:int

class BuyProductsInput(BaseModel):
    bill_id:int
    items_id:list[BayProd]

class TransactionListInput(BaseModel):
    bill_id:Optional[int]
    user_id:Optional[int]
    date_from:Optional[date]
    date_to:Optional[date]