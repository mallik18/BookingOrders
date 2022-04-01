from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.background import BackgroundTasks

from redis_om import get_redis_connection, HashModel, NotFoundError
from starlette.requests import Request
import requests, time

# Fastapi instance
app = FastAPI()

# Fastapi middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods = ['*'],
    allow_headers = ['*']
)

# redis localhost connection
redis_payment = get_redis_connection(
    host = "127.0.0.1",
    port = 6379,
#    db = "redis_payment",
    password = "",
    decode_responses = True

)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str     # pending, completed, refunded

    class Meta:
        database = redis_payment

@app.get("/orders/{pk}")
def get(pk: str):
    return Order.get(pk)

@app.post("/orders",)
async def create(request: Request, background_tasks: BackgroundTasks):     # id , quantity
    body = await request.json()
    req = requests.get("http://localhost:8000/products/%s" % body['id'])
    product = req.json()

    order = Order(
        product_id = body['id'],
        price = product['price'],
        fee = 0.2 * product['price'],
        total = 1.2 * product['price'],
        quantity = body['quantity'],
        status = 'pending'
    )

    order.save()
    
    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()