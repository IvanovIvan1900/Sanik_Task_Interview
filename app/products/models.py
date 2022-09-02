from decimal import Decimal
from enum import unique
from operator import index
from typing import Optional
from app.store.database.gino import db
from dataclasses import dataclass

@dataclass
class Product:
    prod_id: Optional[int] = None
    name: str = None
    description: Optional[str] = None
    price: Decimal = None

    def __repr__(self):
        return f'{self.name}, pr={self.price}'

    @classmethod
    def from_db_model(cls, model) -> Optional["Product"]:
        return cls(prod_id=model.prod_id, name=model.name, description=model.description,
        price = model.price)



class ProductModel(db.Model):
    __tablename__ = "products"

    prod_id = db.Column(db.Integer, nullable = False, primary_key=True)
    name = db.Column(db.String(50), nullable = False, index = True, unique = True)
    description = db.Column(db.Text(), nullable = True)
    price = db.Column(db.Numeric(10,2), nullable = False)

