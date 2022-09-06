import pytest

from app.products.models import Product


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
def list_dict_buy_2(list_db_prod_count_three:list[Product]):
    return [
        {"prod_id": list_db_prod_count_three[0].prod_id, "count":10},
        {"prod_id": list_db_prod_count_three[1].prod_id, "count":5},
    ]

