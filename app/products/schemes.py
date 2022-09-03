from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field

class ProductInput(BaseModel):
    name:str
    description:str = Field("", min_length=0)
    price:str

class ProductOutput(ProductInput):
    prod_id:int

class ListProductInput(BaseModel):
    items:List[ProductInput]

class ListProductOutput(BaseModel):
    info:str
    list_items:List[ProductOutput]

class ListIdInput(BaseModel):
    list_id: List[str] = Field(None)

class ListProductOutput_OnlyInfo(BaseModel):
    info:str
