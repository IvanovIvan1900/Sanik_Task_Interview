import typing
from datetime import datetime
from decimal import Decimal

from app.store.database.base_accessor import BaseAccessor
from app.store.database.gino import db
from app.transactions.models import TransactionModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


class TransAccessor(BaseAccessor):


    async def add_transaction(self, dict_dat:dict)->TransactionModel:
        if dict_dat.get("transaction_id", None) is None and "transaction_id" in dict_dat:
            del dict_dat["transaction_id"]
        result = await insert(TransactionModel).values(**dict_dat).on_conflict_do_nothing().returning(TransactionModel.__table__).gino.first()
        return result

    async def accept_payment(self, transaction_id:int, user_id:int, bill_id:int, amount:int)->str:
        from app.server.server import sanic_app
        from app.users.models import Bill

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
        from app.server.server import sanic_app
        from app.users.models import Bill
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

    async def get_list_transaction(self, date_from:datetime = None, date_to:datetime = None, user_id:int = None, bill_id:int = None)->list[TransactionModel]:
        from app.users.models import BillModel, UserModel

        column = [BillModel.user_id, BillModel.bill_id, UserModel.login, TransactionModel.transaction_id,
                TransactionModel.transaction_date, TransactionModel.amount]
        stmt = select(column)
        stmt = stmt.select_from(TransactionModel.join(BillModel).join(UserModel))
        if date_from is not None:
            stmt = stmt.where(TransactionModel.transaction_date >= date_from)
        if date_to is not None:
            stmt = stmt.where(TransactionModel.transaction_date <= date_to)
        if user_id is not None:
            stmt = stmt.where(BillModel.user_id == user_id)
        if bill_id is not None:
            stmt = stmt.where(BillModel.bill_id == bill_id)

        result = await stmt.gino.all()

        return result
