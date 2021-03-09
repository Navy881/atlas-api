import time
from datetime import datetime, timedelta

from AtlasApi import AtlasApiConnect

url = ''
username = ''
password = ''
atlas_main = AtlasApiConnect(url=url, username=username, password=password)

url = ''
username = ''
password = ''
atlas_carrier = AtlasApiConnect(url=url, username=username, password=password)


CARRIER_ID = '957f5d7c-0cdc-4b88-a8bb-50f289a82c45'

if __name__ == '__main__':
    try:
        atlas_main.start_client()
        atlas_carrier.start_client()

        date_from = '2019-12-21T12:50:00.000Z'
        date_to = '2019-12-21T15:00:00.000Z'

        ################################################################################################################ 
        # TEST: Carrier accepted +1
        ################################################################################################################
        order = atlas_main.create_order(hub_code='01-01-КЛМ', leg_external_id='',
                                        delivery_from=date_from, delivery_to=date_to)
        # if order is not None:
        #     print('Order:', order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        route = atlas_main.get_route_by_order_id(order_id=order['Id'])

        carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_before = carrier_karma_before['KarmaValue']

        route_id = ''
        if route is not None:
            route_id = route[0]['Id']
            # print('Route:', route_id, route[0]['RouteInfo']['Name'])

            atlas_main.assign_carrier_on_route(route_id=route_id, carrier_id=CARRIER_ID)
            time.sleep(1)
            atlas_carrier.set_route_state(route_id=route_id, route_state='CarrierAccepted')
            time.sleep(5)

        print('Carrier karma: ' + str(carrier_karma_before))
        carrier_karma_after = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_after = carrier_karma_after['KarmaValue']
        print('Carrier karma: ' + str(carrier_karma_after))

        if carrier_karma_before + 1 == carrier_karma_after:
            print('Carrier accepted Karma +1: SUCCESS\n')
        else:
            print('\nCarrier accepted Karma +1: FAILED \nRoute: {}\nCarrier: {}\n'.format(route_id, CARRIER_ID))

        ################################################################################################################ 
        # TEST: Carrier rejected -5
        ################################################################################################################
        order = atlas_main.create_order(hub_code='01-01-КЛМ', leg_external_id='',
                                        delivery_from=date_from, delivery_to=date_to)
        # if order is not None:
        #     print('Order:', order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        route = atlas_main.get_route_by_order_id(order_id=order['Id'])

        carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_before = carrier_karma_before['KarmaValue']

        route_id = ''
        if route is not None:
            route_id = route[0]['Id']
            # print('Route:', route_id, route[0]['RouteInfo']['Name'])

            atlas_main.assign_carrier_on_route(route_id=route_id, carrier_id=CARRIER_ID)
            time.sleep(1)
            atlas_carrier.remove_carrier_from_route(route_id=route_id)
            time.sleep(5)

        print('Carrier karma: ' + str(carrier_karma_before))
        carrier_karma_after = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_after = carrier_karma_after['KarmaValue']
        print('Carrier karma: ' + str(carrier_karma_after))

        if carrier_karma_before - 5 == carrier_karma_after:
            print('Carrier rejected Karma -5: SUCCESS\n')
        else:
            print('\nCarrier rejected Karma -5: FAILED \nRoute: {}\nCarrier: {}\n'.format(route_id, CARRIER_ID))

        ################################################################################################################ 
        # TEST: Carrier rejected after accepting -5
        ################################################################################################################
        order = atlas_main.create_order(hub_code='01-01-КЛМ', leg_external_id='',
                                        delivery_from=date_from, delivery_to=date_to)
        # if order is not None:
        #     print('Order:', order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        route = atlas_main.get_route_by_order_id(order_id=order['Id'])

        carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_before = carrier_karma_before['KarmaValue']

        route_id = ''
        if route is not None:
            route_id = route[0]['Id']
            # print('Route:', route_id, route[0]['RouteInfo']['Name'])

            atlas_main.assign_carrier_on_route(route_id=route_id, carrier_id=CARRIER_ID)
            time.sleep(1)
            atlas_carrier.set_route_state(route_id=route_id, route_state='CarrierAccepted')
            time.sleep(5)

            carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
            carrier_karma_before = carrier_karma_before['KarmaValue']

            atlas_carrier.remove_carrier_from_route(route_id=route_id)
            time.sleep(5)

        print('Carrier karma: ' + str(carrier_karma_before))
        carrier_karma_after = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_after = carrier_karma_after['KarmaValue']
        print('Carrier karma: ' + str(carrier_karma_after))

        if carrier_karma_before - 10 == carrier_karma_after:
            print('Carrier rejected after accepting Karma -10: SUCCESS\n')
        else:
            print('\nCarrier rejected after accepting Karma -10: FAILED \nRoute: {}\nCarrier: {}\n'.format(route_id, CARRIER_ID))

        ################################################################################################################ 
        # TEST: Carrier picked up route +4
        ################################################################################################################
        order = atlas_main.create_order(hub_code='01-01-КЛМ', leg_external_id='',
                                        delivery_from=date_from, delivery_to=date_to)
        # if order is not None:
            # print('Order:', order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        route = atlas_main.get_route_by_order_id(order_id=order['Id'])


        route_id = ''
        if route is not None:
            route_id = route[0]['Id']
            # print('Route:', route_id, route[0]['RouteInfo']['Name'])

            atlas_main.assign_carrier_on_route(route_id=route_id, carrier_id=CARRIER_ID)
            time.sleep(1)
            atlas_carrier.remove_carrier_from_route(route_id=route_id)
            time.sleep(5)

        carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_before = carrier_karma_before['KarmaValue']

        atlas_main.assign_carrier_on_route(route_id=route_id, carrier_id=CARRIER_ID)
        time.sleep(5)

        print('Carrier karma: ' + str(carrier_karma_before))
        carrier_karma_after = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_after = carrier_karma_after['KarmaValue']
        print('Carrier karma: ' + str(carrier_karma_after))

        if carrier_karma_before + 4 == carrier_karma_after:
            print('Carrier picked up route Karma +4: SUCCESS\n')
        else:
            print('\nCarrier picked up route Karma +4: FAILED \nRoute: {}\nCarrier: {}\n'.format(route_id, CARRIER_ID))

        ################################################################################################################
        # TEST: Carrier won bidding +4
        ################################################################################################################
        order = atlas_main.create_order(hub_code='01-01-КЛМ', leg_external_id='test_direction_1',
                                        delivery_from=date_from, delivery_to=date_to)
        # if order is not None:
        #     print('Order:', order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        route = atlas_main.get_route_by_order_id(order_id=order['Id'])

        carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_before = carrier_karma_before['KarmaValue']

        route_id = ''
        if route is not None:
            route_id = route[0]['Id']
            # print('Route:', route_id, route[0]['RouteInfo']['Name'])
            lot_start = datetime.now() - timedelta(hours=3)
            lot_end = lot_start + timedelta(minutes=1)
            lot_start = lot_start.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            lot_end = lot_end.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            lot = atlas_main.create_lot(route_id=route_id, lot_start=lot_start, lot_end=lot_end)
            time.sleep(5)
            atlas_carrier.create_bet(lot_id=lot['Id'], bet_value=100)
            time.sleep(60)

        print('Carrier karma: ' + str(carrier_karma_before))
        carrier_karma_after = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_after = carrier_karma_after['KarmaValue']
        print('Carrier karma: ' + str(carrier_karma_after))

        if carrier_karma_before + 4 == carrier_karma_after:
            print('Carrier won bidding Karma +4: SUCCESS\n')
        else:
            print('\nCarrier won bidding Karma +4: FAILED \nRoute: {}\nCarrier: {}\n'.format(route_id, CARRIER_ID))

        ################################################################################################################
        # TEST: Carrier auto rejected +4
        ################################################################################################################
        order = atlas_main.create_order(hub_code='01-01-КЛМ', leg_external_id='test_direction_1',
                                        delivery_from=date_from, delivery_to=date_to)
        # if order is not None:
        #     print('Order:', order['Id'], order['OrderInfo']['ExternalId'])
        time.sleep(7)
        route = atlas_main.get_route_by_order_id(order_id=order['Id'])

        carrier_karma_before = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_before = carrier_karma_before['KarmaValue']

        route_id = ''
        if route is not None:
            route_id = route[0]['Id']
            # print('Route:', route_id, route[0]['RouteInfo']['Name'])
            atlas_main.auto_assign(route_id=route_id)
            time.sleep(100)

        print('Carrier karma: ' + str(carrier_karma_before))
        carrier_karma_after = atlas_main.get_carrier_karma(carrier_id=CARRIER_ID)
        carrier_karma_after = carrier_karma_after['KarmaValue']
        print('Carrier karma: ' + str(carrier_karma_after))

        if carrier_karma_before - 5 == carrier_karma_after:
            print('Carrier auto rejected Karma -5: SUCCESS\n')
        else:
            print('\nCarrier auto rejected Karma -5: FAILED \nRoute: {}\nCarrier: {}\n'.format(route_id, CARRIER_ID))


    except Exception as e:
        print(e)
