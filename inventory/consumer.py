from main import redis_conn, Product
import time

key = 'order_completed'
group = 'inventory-group'

try:
    redis_conn.xgroup_create(key, group)
except:
    print("Group already exists!!")

while True:
    try:
        results = redis_conn.xreadgroup(group, key, {key: '>'}, None)  # '>' : means we want to get all the events
        
        print(results)
    except Exception as e:
        print(str(e))

    time.sleep(1)