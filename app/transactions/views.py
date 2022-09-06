from app.server.server import sanic_app
from app.transactions.models import TransactionModel
from app.transactions.schemes import BuyProductsInput, PaymentInputs, PaymentOuput
from app.transactions.utils import get_signature
from app.users.auth import authorized, is_admin
from sanic.request import Request
from sanic.response import json, text
from sanic_openapi import openapi
from sanic_openapi.openapi3.definitions import RequestBody, Response
from sanic_pydantic import webargs


@sanic_app.post("/payment/webhook", name='payment.webhook')
@openapi.description('Payments to bill')
@openapi.definition(
    body=RequestBody(PaymentInputs, required=True),
    response=[Response(PaymentOuput)],
)
@authorized
@is_admin
@webargs(body=PaymentInputs)
async def payment(request:Request, **kwargs)->json:
    status_ret = 200
    dict_result = {
        "info": "",
    }
    signature = kwargs['payload']['signature'].strip()
    transaction_id = kwargs['payload']['transaction_id']
    user_id = kwargs['payload']['user_id']
    bill_id = kwargs['payload']['bill_id']
    amount = kwargs['payload']['amount']
    correct_signature = await get_signature(transaction_id=transaction_id, user_id=user_id, bill_id=bill_id, amount=amount)
    if correct_signature != signature:
        status_ret = 400
        dict_result["info"] = "signature is not correct"
        return json(dict_result, status=status_ret)
    else:
        error_description = await sanic_app.config["STORE"].trans_accessor.accept_payment(transaction_id=transaction_id,
                     user_id=user_id, bill_id=bill_id, amount=amount)
        if error_description:
            status_ret = 400
            dict_result["info"] = error_description

    return json(dict_result, status=status_ret)

@sanic_app.post("/transaction/buy", name='transaction.buy')
@openapi.description('Buy products. If id prod not found, price is 0')
@openapi.definition(
    body=RequestBody(BuyProductsInput, required=True),
    response=[Response(PaymentOuput)],
)
@authorized
@is_admin
@webargs(body=BuyProductsInput)
async def transaction_buy(request:Request, **kwargs)->json:
    status_ret = 200
    dict_result = {
        "info": "",
    }
    items = kwargs['payload']['items_id']
    bill_id = kwargs['payload']['bill_id']
    list_id = [elem["prod_id"] for elem in items]
    amount = 0
    list_prod_bd = await sanic_app.config["STORE"].prod_accessor.get_list_of_prod_wich_id(list_id=list_id)
    dict_of_price = dict((elem.prod_id, elem.price) for elem in list_prod_bd)
    for elem in items:
        price = dict_of_price.get(elem["prod_id"], 0)
        amount += price*elem["count"]
    error_description = await sanic_app.config["STORE"].trans_accessor.buy_transaction(bill_id=bill_id, amount=amount)
    if error_description:
        status_ret = 400
        dict_result["info"] = error_description

    return json(dict_result, status= status_ret)