from decimal import Decimal
import pytest
from app.transactions.utils import get_signature
from tests.fixtures.users import get_db_bill_one_for_user, get_header_auth_wich_user
import typing
from app.users.models import User
import json
from tests.fixtures.general import run_corootine_in_current_loop

if typing.TYPE_CHECKING:
    from sanic_testing.reusable import ReusableClient
    from sanic import Sanic

class TestTransactions():

    def test_accepted_payment(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, dict_trans_one_payment_100:dict,
                dict_trans_one_payment_10:dict):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        url = test_app.url_for('payment.webhook')
        dict_trans_one_payment_100["user_id"] = db_user_admin.user_id
        dict_trans_one_payment_100["signature"] = run_corootine_in_current_loop(get_signature(**dict_trans_one_payment_100))
        data = json.dumps(dict_trans_one_payment_100)
        _, response = cli.post(url, headers=headers, data=data)
        assert 200 == response.status
        bill_bd = run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.get_bill_by_id(dict_trans_one_payment_100["bill_id"]))
        assert dict_trans_one_payment_100["amount"] == bill_bd.amount

        dict_trans_one_payment_10["user_id"] = db_user_admin.user_id
        dict_trans_one_payment_10["signature"] = run_corootine_in_current_loop(get_signature(**dict_trans_one_payment_10))
        data = json.dumps(dict_trans_one_payment_10)
        _, response = cli.post(url, headers=headers, data=data)
        assert 200 == response.status
        bill_bd = run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.get_bill_by_id(dict_trans_one_payment_10["bill_id"]))
        assert 110 == bill_bd.amount

    def test_not_correct_signature(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, dict_trans_one_payment_100:dict):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        url = test_app.url_for('payment.webhook')
        dict_trans_one_payment_100["user_id"] = db_user_admin.user_id
        dict_trans_one_payment_100["signature"] = run_corootine_in_current_loop(get_signature(**dict_trans_one_payment_100))
        dict_trans_one_payment_100["amount"] = 150
        data = json.dumps(dict_trans_one_payment_100)
        _, response = cli.post(url, headers=headers, data=data)
        assert 400 == response.status
        assert "signature is not correct" == response.json["info"]

    def test_buy_success(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, dict_trans_one_payment_100:dict, 
            list_dict_buy_2:list[dict], dict_bill_one:dict):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        bill_db = get_db_bill_one_for_user(test_app=test_app, user=db_user_admin, dict_bill=dict_bill_one, amount=800)
        dict_trans_one_payment_100["bill_id"] = bill_db.bill_id
        url = test_app.url_for('transaction.buy')
        dict_input  = {
            "bill_id":dict_trans_one_payment_100["bill_id"],
            "items_id":list_dict_buy_2,
        }
        data = json.dumps(dict_input)
        _, response = cli.post(url, headers=headers, data=data)
        assert 200 == response.status


    def test_buy_success_less_than_amount_on_bill(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, dict_trans_one_payment_100:dict, 
            list_dict_buy_2:list[dict], dict_bill_one:dict):
        headers = get_header_auth_wich_user(db_user_admin.user_id)
        amount = 600
        bill_db = get_db_bill_one_for_user(test_app=test_app, user=db_user_admin, dict_bill=dict_bill_one, amount=amount)
        dict_trans_one_payment_100["bill_id"] = bill_db.bill_id
        url = test_app.url_for('transaction.buy')
        dict_input  = {
            "bill_id":dict_trans_one_payment_100["bill_id"],
            "items_id":list_dict_buy_2,
        }
        data = json.dumps(dict_input)
        _, response = cli.post(url, headers=headers, data=data)
        assert 400 == response.status
        amount_prod = Decimal('700.00')
        assert f'There are not enough funds in the account. On bill {amount}, necessary {amount_prod}.' == response.json["info"]
