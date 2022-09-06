from decimal import Decimal
import typing
from app.transactions.models import TransactionModel

from app.store.database.base_accessor import BaseAccessor
from app.store.database.gino import db
from sqlalchemy.dialects.postgresql import insert

if typing.TYPE_CHECKING:
    from sanic import Sanic


class TransAccessor(BaseAccessor):
    

    async def add_transaction(self, dict_dat:dict)->TransactionModel:
        result = await insert(TransactionModel).values(**dict_dat).on_conflict_do_nothing().returning(TransactionModel.__table__).gino.first()
        return result

    async def accept_payment(self, transaction_id:int, user_id:int, bill_id:int, amount:int)->str:
        from app.users.models import Bill
        from app.server.server import sanic_app

        error_description = ""
        summ = Decimal(amount)
        async with db.transaction() as tx:
            bill_bd = await sanic_app.config["STORE"].user_accessor.create_bill_if_not_exist(Bill(bill_id=bill_id, amount=Decimal('0.0'), user_id=user_id))
            if bill_bd is not None:
                dict_data = {
                    "transaction_id": transaction_id, 
                    "bill_id": bill_id,
                    "amount": summ,
                }
                transaction_db = await self.add_transaction(dict_data)
                if transaction_db:
                    result = await sanic_app.config["STORE"].user_accessor.add_amount_to_bill(bill_bd.bill_id, summ)
                else:
                    error_description = "error create transaction"
            else:
                error_description = "error create bill"
        return error_description

    async def buy_transaction(self, bill_id:int, amount:int)->str:
        from app.users.models import Bill
        from app.server.server import sanic_app
        error_description = ""
        bill_bd = await sanic_app.config["STORE"].user_accessor.get_bill_by_id(bill_id=bill_id)
        if bill_bd:
            if int(bill_bd.amount) < amount:
                error_description = f'There are not enough funds in the account. On bill {int(bill_bd.amount)}, necessary {amount}.'
            else:
                async with db.transaction() as tx:
                    dict_data = {
                        "bill_id": bill_bd.bill_id,
                        "amount": -amount,
                    }
                    transaction_db = await self.add_transaction(dict_data)
                    if transaction_db:
                        result = await sanic_app.config["STORE"].user_accessor.add_amount_to_bill(bill_bd.bill_id, -amount)
                    else:
                        error_description = "error create transaction"

        else:
            error_description = f'Bill wich bill_id {bill_id} is not exist'

        return error_description
    