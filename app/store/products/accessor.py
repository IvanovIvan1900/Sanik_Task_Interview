import typing
from decimal import Decimal

from app.products.models import Product, ProductModel
from app.store.database.base_accessor import BaseAccessor
from sqlalchemy.dialects.postgresql import insert


class ProdAccessor(BaseAccessor):


    async def add_list_of_prod(self, list_of_data:list[dict])->list[Product]:
        for elem in list_of_data:
            if isinstance(elem.get('price'), str):
                elem['price'] = Decimal(elem.get('price'))
        stmt = insert(ProductModel).values(list_of_data)
        stmt = stmt.on_conflict_do_update(index_elements=["name"],set_={
                        "description":stmt.excluded.description,
                        "price":stmt.excluded.price,
                        })
        query = await stmt.returning(ProductModel.__table__).gino.all()
        return [Product.from_db_model(elem) for elem in query]

    async def get_list_of_prod(self)->list[ProductModel]:
        return await ProductModel.query.gino.all()

    async def del_list_of_id(self, list_of_id:list[int])->list[ProductModel]:
        return await ProductModel.delete.where(ProductModel.prod_id.in_(list_of_id)).gino.status()

    async def get_list_of_prod_wich_id(self, list_id:list[int])->list[ProductModel]:
        return await ProductModel.query.where(ProductModel.prod_id.in_(list_id)).gino.all()
