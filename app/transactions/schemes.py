
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

class TransactionListOutputItem(BaseModel):
    amount:str
    bill_id:int
    transaction_date:str
    user_id:int
    login:str
    transaction_id:int

class TransactionListOutput(BaseModel):
    items:list[TransactionListOutputItem]

class ListBillsInput(BaseModel):
    bill_id:Optional[int]
    user_id:Optional[int]

class ListBillsItem(BaseModel):
    bill_id:int
    amount:int

class ListUsersBillItem(BaseModel):
    users_id:int
    bills:list[ListBillsItem]

class ListBillsOutput(BaseModel):
    items:list[ListUsersBillItem]
