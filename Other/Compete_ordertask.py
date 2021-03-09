
import datetime
from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''

order_task_id = '548f7491-a556-4164-a3cf-a988e71455b3'

if __name__ == '__main__':
    try:
        atlas = AtlasApiConnect(url=stand, username=username, password=password)
        atlas.start_client()
        atlas.complete_delivery_order_task(order_task_id=order_task_id)
    except Exception as e:
        print(e)
