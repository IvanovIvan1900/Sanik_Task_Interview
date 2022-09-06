from ast import List
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