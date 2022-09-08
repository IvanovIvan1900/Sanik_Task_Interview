from decimal import Decimal
import pytest
import typing
from app.transactions.models import TransactionModel
from app.products.models import ProductModel
from app.users.models import Bill
from tests.fixtures.general import run_corootine_in_current_loop

if typing.TYPE_CHECKING:
    from sanic import Sanic


@pytest.fixture
def dict_trans_one_payment_100(dict_bill_one:dict)->dict:
    return {
        "transaction_id": '123465789',
        "bill_id":dict_bill_one.get("bill_id"),
        "amount": 100,
    }

@pytest.fixture
def dict_trans_one_payment_10(dict_bill_one:dict)->dict:
    return {
        "transaction_id": '987654321',
        "bill_id":dict_bill_one.get("bill_id"),
        "amount": 10,
    }

@pytest.fixture
def dict_trans_two_payment_100(dict_bill_two:dict)->dict:
    return {
        "transaction_id": '12369874',
        "bill_id":dict_bill_two.get("bill_id"),
        "amount": 100,
    }

@pytest.fixture
def list_dict_buy_2(list_db_prod_count_three:list[ProductModel])->list[dict]:
    return [
        {"prod_id": list_db_prod_count_three[0].prod_id, "count":10},
        {"prod_id": list_db_prod_count_three[1].prod_id, "count":5},
    ]

@pytest.fixture
def list_dict_transactions_10()->list[dict]:
    return [
        {
            "amount":Decimal('10.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('50.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('-30.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('25.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('-15.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('-5.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('170.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('100.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('58.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
        {
            "amount":Decimal('-30.00'),
            "bill_id":None,
            "transaction_id":None,
            "transaction_date":None,
        },
    ]

def create_transaction_from_list(test_app: "Sanic", list_trans_input:list[dict], list_of_bill:list[dict])->list[TransactionModel]:
    list_output:list[TransactionModel] = []
    for elem in list_of_bill:
        run_corootine_in_current_loop(test_app.config["STORE"].user_accessor.create_bill_if_not_exist(Bill(**elem)))

    for elem in list_trans_input:
        list_output.append(run_corootine_in_current_loop(test_app.config["STORE"].trans_accessor.add_transaction(elem)))

    return list_output