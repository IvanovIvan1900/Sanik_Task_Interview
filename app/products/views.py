from typing import Any, Callable
from app.server.server import sanic_app
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_openapi import openapi
from sanic_openapi.openapi3.definitions import RequestBody, Response
from sanic_pydantic import webargs
from app.products.schemes import ListIdInput, ListProductInput, ListProductOutput, ListProductOutput_OnlyInfo
from app.users.auth import (authorized,is_admin)
from sanic import Blueprint

@sanic_app.post("/products/", name='products')
@openapi.description('Add list of produts if name always in user - update description and price')
@openapi.definition(
    body=RequestBody(ListProductInput, required=True),
    response=[Response(ListProductOutput)],
)
@is_admin
@authorized
@webargs(body=ListProductInput)
async def post(request:Request, **kwargs)->json:
    dic_result = {
        "info":"ok",
        "list_items":[],
    }
    list_of_items = kwargs['payload']['items']
    status_res = 200
    if len(list_of_items) > 0:
        result = await sanic_app.config["STORE"].prod_accessor.add_list_of_prod(list_of_items)
        dic_result["list_items"] = [elem.__dict__ for elem in result]
    return json(dic_result,status=status_res)


@sanic_app.get("/products/", name='products')
@openapi.description('Get list existing producs')
@openapi.definition(
    # body=RequestBody(ListProductInput, required=True),
    response=[Response(ListProductOutput)],
)
@is_admin
@authorized
async def get(request:Request, **kwargs)->json:
    dic_result = {
        "info":"ok",
        "list_items":[],
    }
    status_res = 200
    result = await sanic_app.config["STORE"].prod_accessor.get_list_of_prod()
    dic_result["list_items"] = [elem.__dict__['__values__'] for elem in result]
    return json(dic_result,status=status_res)


@sanic_app.delete("/products/", name='products')
@openapi.description('Delete element. Get list id. If if is not exist not delete items')
@openapi.definition(
    body=RequestBody(ListIdInput, required=True),
    response=[Response(ListProductOutput_OnlyInfo)],
)
@is_admin
@authorized
# @webargs(query=ListIdInput)
async def delete(request:Request)->json:
    dic_result = {
        "info":"ok",
    }
    status_res = 200
    try:
        list_id = [int(elem) for elem in request.args.getlist("list_id")]
    except ValueError as ve:
        list_id = []
        status_res = 400
        dic_result["info"] = f'not correct id. Error is "{ve}"'
    if len(list_id) > 0:
        result = await sanic_app.config["STORE"].prod_accessor.del_list_of_id(list_id)
    return json(dic_result,status=status_res)

# class ProductsManager(HTTPMethodView):
#     decorators: list[Callable[[Callable[..., Any]], Callable[..., Any]]]=[
#         openapi.description('Work wich product'),
#         authorized,
#         is_admin,
#         ]

#     @staticmethod
#     # @openapi.definition(
#     #     body=RequestBody(ListProductInput, required=True),
#     #     # response=[Response(LoginResponse)],
#     # )
#     @webargs(body=ListProductInput)
#     async def post(request:Request, **kwargs)->json:
#         a = 4

# sanic_app.add_route(ProductsManager.as_view(), '/products')

