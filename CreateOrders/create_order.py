import time
from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''
atlas = AtlasApiConnect(url=stand, username=username, password=password)

LEG_EXTERNAL_ID = 'ATL-4239'
DATE_FROM = '2020-04-23T12:50:00.000Z'
DATE_TO = '2020-04-23T15:00:00.000Z'
LOAD_FROM = '2019-12-03T00:00:00.000Z'
LOAD_TO = '2019-12-03T23:59:59.000Z'

if __name__ == '__main__':
    try:
        order_ids = []
        atlas.start_client()
        orders_count = input('Enter orders quantity = ')
        for i in range(int(orders_count)):

            if username == 'cedrus@cargoonline.ru':
                order = atlas.create_order(hub_code='01-01-КЛМ', leg_external_id=LEG_EXTERNAL_ID,
                                           delivery_from=DATE_FROM, delivery_to=DATE_TO,
                                           load_from=LOAD_FROM, load_to=LOAD_TO)

            elif username == 'manager@belugagroup.ru':
                # order = atlas.create_order(delivery_from=DATE_FROM, hub_code='DefaultCode', delivery_to=DATE_TO,
                #                            load_from=LOAD_FROM, load_to=LOAD_TO)

                order = atlas.create_order(hub_code='DefaultCode', delivery_from=DATE_FROM, delivery_to=DATE_TO)

            if order is not None:
                order_ids.append(order['Id'])
                print(order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        for order_id in order_ids:
            route = atlas.get_route_by_order_id(order_id=order_id)
            if route is not None:
                print(route[0]['Id'], route[0]['RouteInfo']['Name'])
    except Exception as e:
        print(e)
