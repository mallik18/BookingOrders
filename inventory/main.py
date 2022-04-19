from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis_om import get_redis_connection, HashModel, NotFoundError

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
redis_conn = get_redis_connection(
    host = "localhost",
    port = 6379,
    password = "",
    decode_responses = True

)

class Product(HashModel):
    """ Product class which holds product data """
    name : str
    price : float
    quantity : int

    class Meta:
        database = redis_conn

@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post('/products')
def create(product: Product):
    return product.save()

@app.get('/products/{pk}')
def get(pk: str):
    try:
        return Product.get(pk)
    except NotFoundError:   #redis exception
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error": "There goes my error"},)   # HTTPExecption from fastapi


@app.delete('/products/{pk}')
def delete(pk: str):
    if(Product.delete(pk)):     # delete a particular item with key if present return 1
        return JSONResponse("Item deleted", status_code= 200)
    else:
        return JSONResponse("Item not found", status_code= 400)