import json
import typing
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from unittest.mock import ANY

import pytest
from app.transactions.utils import get_signature
from app.users.models import User, Bill
from tests.fixtures.general import run_corootine_in_current_loop
from tests.fixtures.transactions import create_transaction_from_list
from tests.fixtures.users import (get_db_bill_one_for_user,
                                  get_header_auth_wich_user)

if typing.TYPE_CHECKING:
    from sanic import Sanic
    from sanic_testing.reusable import ReusableClient

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

    def service_fill_param_in_list(self, list_of_transactions:list[dict], bill_id:int, transaction_date:datetime, index_from:int, index_to:int):
        for i in range(index_from, index_to):
            list_of_transactions[i]["bill_id"] = bill_id
            list_of_transactions[i]["transaction_date"] = transaction_date

    def service_list_transaction_create_data(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, db_user_1_activate:User, dict_bill_one:dict,
            dict_bill_two:dict, dict_bill_three:dict, list_dict_transactions_10:list[dict]):

        date_yesterday = datetime.now()-timedelta(days=1)
        date_today = datetime.now()
        dict_bill_one["user_id"] = db_user_admin.user_id
        dict_bill_two["user_id"] = db_user_admin.user_id
        dict_bill_three["user_id"] = db_user_1_activate.user_id
        index_from = 0
        index_to = 3
        self.service_fill_param_in_list(list_dict_transactions_10, index_from=index_from, index_to=index_to, bill_id=dict_bill_one["bill_id"], transaction_date=date_today)
        index_from = index_to
        index_to = 5
        self.service_fill_param_in_list(list_dict_transactions_10, index_from=index_from, index_to=index_to, bill_id=dict_bill_one["bill_id"], transaction_date=date_yesterday)
        index_from = index_to
        index_to = 7
        self.service_fill_param_in_list(list_dict_transactions_10, index_from=index_from, index_to=index_to, bill_id=dict_bill_two["bill_id"], transaction_date=date_today)
        index_from = index_to
        index_to = 8
        self.service_fill_param_in_list(list_dict_transactions_10, index_from=index_from, index_to=index_to, bill_id=dict_bill_three["bill_id"], transaction_date=date_today)
        index_from = index_to
        index_to = 10
        self.service_fill_param_in_list(list_dict_transactions_10, index_from=index_from, index_to=index_to, bill_id=dict_bill_three["bill_id"], transaction_date=date_yesterday)

        create_transaction_from_list(test_app=test_app, list_trans_input=list_dict_transactions_10, list_of_bill=[dict_bill_one, dict_bill_two, dict_bill_three])

    def service_list_transaction_get_filtered_list(self, list_transaction:list[dict], list_bill:list[dict], filters:dict
            , list_of_user:User)->list[dict]:
        dict_bill_id_to_user_id = {elem["bill_id"]:elem["user_id"] for elem in list_bill}
        dict_user_id_to_login = {elem.user_id:elem.login for elem in list_of_user}
        set_of_bills = None
        list_of_result = []
        if filters.get("date_from", None) is not None:
            filters["date_from"] = datetime.combine(filters["date_from"], time.min)
        if filters.get("date_to", None) is not None:
            filters["date_to"] = datetime.combine(filters["date_to"], time.max)
        if filters.get("user_id", None) is not None or filters.get("bill_id", None) is not None:
            set_of_bills = set()
            if filters.get("user_id", None) is not None:
                set_of_bill_for_user_id = {elem["bill_id"] for elem in list_bill if elem["user_id"] == filters["user_id"]}
            else:
                set_of_bill_for_user_id = {elem["bill_id"] for elem in list_bill}
            if filters.get("bill_id", None) is not None:
                set_of_bills_for_bills_id = {elem["bill_id"] for elem in list_bill if elem["bill_id"] == filters["bill_id"]}
            else:
                set_of_bills_for_bills_id = {elem["bill_id"] for elem in list_bill}
            set_of_bills = set_of_bill_for_user_id.intersection(set_of_bills_for_bills_id)

        for elem in list_transaction:
            if filters.get("date_from", None) is not None:
                if elem["transaction_date"] < filters.get("date_from", None):
                    continue
            if filters.get("date_to", None) is not None:
                if elem["transaction_date"] > filters.get("date_to", None):
                    continue
            if set_of_bills is not None and elem["bill_id"] not in set_of_bills:
                continue
            elem_add = elem.copy()
            elem_add["user_id"] =dict_bill_id_to_user_id.get(elem_add["bill_id"], None)
            elem_add["login"] = dict_user_id_to_login.get(elem_add["user_id"], None)
            elem_add["transaction_date"] = elem_add["transaction_date"].isoformat()
            elem_add["transaction_id"] = ANY
            elem_add["amount"] = str(elem_add["amount"])
            list_of_result.append(elem_add)

        return list_of_result

    @pytest.mark.parametrize("date_from, date_to, user, bill",
            [
                (None,None,None,None),
                (pytest.lazy_fixture("date_today"),pytest.lazy_fixture("date_today"), None, None),
                (pytest.lazy_fixture("date_today"),pytest.lazy_fixture("date_today"), None, pytest.lazy_fixture("dict_bill_one")),
                (pytest.lazy_fixture("date_today"),pytest.lazy_fixture("date_today"), pytest.lazy_fixture("db_user_admin"), None),
                (pytest.lazy_fixture("date_today"),pytest.lazy_fixture("date_today"), pytest.lazy_fixture("db_user_admin"), pytest.lazy_fixture("dict_bill_one")),
                (pytest.lazy_fixture("date_yesterday"),pytest.lazy_fixture("date_today"), pytest.lazy_fixture("db_user_admin"), pytest.lazy_fixture("dict_bill_one")),
            ]
        )
    def test_list_transaction(self, cli: "ReusableClient", test_app: "Sanic", db_user_admin:User, db_user_1_activate:User, dict_bill_one:dict,
            dict_bill_two:dict, dict_bill_three:dict, list_dict_transactions_10:list[dict],
            date_from:date, date_to:date , user:User, bill:Bill):
        headers = get_header_auth_wich_user(db_user_admin.user_id)

        data_query = {}
        if date_from is not None:
            data_query["date_from"] = date_from
        if date_to is not None:
            data_query["date_to"] = date_to
        if user is not None:
            data_query["user_id"] = user.user_id
        if bill is not None:
            data_query["bill_id"] = bill["bill_id"]

        self.service_list_transaction_create_data(cli, test_app, db_user_admin, db_user_1_activate, dict_bill_one, dict_bill_two, 
                    dict_bill_three, list_dict_transactions_10)
        url = test_app.url_for('transaction.get.list', **data_query)
        _, response = cli.get(url, headers=headers)

        assert 200 == response.status
        json_data = json.loads(response.json)
        etalon_date = self.service_list_transaction_get_filtered_list(list_transaction=list_dict_transactions_10, list_bill=[dict_bill_one, dict_bill_two, dict_bill_three], 
                    filters=data_query, list_of_user=[db_user_admin, db_user_1_activate])
        assert len(etalon_date) == len(json_data["items"])
        key_func = lambda x: (x["user_id"], x["bill_id"],x["transaction_date"])
        for elem_etalon, elem_db in zip(sorted(etalon_date, key=key_func), sorted(json_data["items"], key=key_func)):
            assert elem_etalon == elem_db
