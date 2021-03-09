
import datetime
import time
import random
from AtlasApi import AtlasApiConnect

stand = ''

username = ''
password = ''

performer_username_1 = ''
performer_password_1 = ''

performer_username_2 = ''
performer_password_2 = ''


date = '2021-02-04'
longitude = '37.608392'
latitude = '55.864951'


def create_delivery_order(time_slot_from: str, time_slot_to: str, hub_code: str, carrier_id: str,
                          performer_id: str, transport_id: str):
    result = None

    order = atlas.create_delivery_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                        hub_code=hub_code,
                                        # carrier_code=carrie_code,
                                        # transport_number=transport_number,
                                        delivery_from=time_slot_from,
                                        delivery_to=time_slot_to,
                                        longitude=longitude,
                                        latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(7)

        route = atlas.get_route_by_order_id(order_id=order["Id"])
        if route is not None:
            print('INFO: Create route ' + route[0]['RouteInfo']['Name'] + ' [' + route[0]['Id'] + '] for order ' +
                  order['OrderInfo']['Number'])

            response = atlas.assign_carrier_on_route(route_id=route[0]['Id'], carrier_id=carrier_id)

            if response is not None:
                print('INFO: On route ' + route[0]['RouteInfo']['Name'] + ' assigned carrier ' + carrier_id)

                time.sleep(1)
                response = atlas.assign_performer_on_route(route_id=route[0]['Id'],
                                                           transport_id=transport_id,
                                                           performer_id=performer_id)

                if response is not None:
                    print('INFO: On route ' + route[0]['RouteInfo']['Name'] + ' assigned performer ' + performer_id)
                    result = order

    return result


def create_pickup_order(time_slot_from: str, time_slot_to: str, hub_code: str, carrier_id: str,
                        performer_id: str, transport_id: str):
    result = None

    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000, 99999)),
                                      hub_code=hub_code,
                                      # carrier_code=carrie_code,
                                      # transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    assert order is not None, 'Order creating failed'

    print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

    time.sleep(7)
    route = atlas.create_route(route_name=f"Route_{order['OrderInfo']['Number']}",
                               route_start=order['PickupTimeSlot']['From'],
                               route_end=order['PickupTimeSlot']['To'])

    assert route is not None

    time.sleep(1)
    route_point = atlas.create_route_point(route_id=route['Id'],
                                           point_type='PickUp',
                                           point_latitude=order['LocationInfo']['Latitude'],
                                           point_longitude=order['LocationInfo']['Longitude'],
                                           point_order=1,
                                           planning_time=order['PickupTimeSlot']['From'])

    assert route_point is not None

    time.sleep(1)
    response = atlas.create_order_task(route_point_id=route_point['Id'], order_id=order['Id'])

    assert response is not None

    response = atlas.set_route_state(route_id=route['Id'], route_state='Planned')

    assert response is not None, 'Route creating failed'

    print('INFO: Create route ' + route['RouteInfo']['Name'] + ' [' + route['Id'] + '] for order ' +
          order['OrderInfo']['Number'])

    time.sleep(1)
    response = atlas.assign_carrier_on_route(route_id=route['Id'], carrier_id=carrier_id)

    assert response is not None

    print('INFO: On route ' + route['RouteInfo']['Name'] + ' assigned carrier ' + carrier_id)

    time.sleep(1)
    response = atlas.assign_performer_on_route(route_id=route['Id'],
                                               transport_id=transport_id,
                                               performer_id=performer_id)

    assert response is not None
    print('INFO: On route ' + route['RouteInfo']['Name'] + ' assigned performer ' + performer_id)

    result = order

    return result


# 1 Выполняемый заказ на доставку вовремя
def start_order_in_time(order: dict, performer_atlas: AtlasApiConnect):
    response = atlas.update_order_state(order["Id"], 'OnItsWay')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': OnItsWay')

    response = performer_atlas.create_eta_for_order(order["Id"], date + 'T18:30:00.000Z')
    if response is not None:
        print('INFO: Created new ETA for order ' + order['OrderInfo']['Number'])

    time.sleep(1)


# 3 Выполняемый заказ на доставку c опозданием
def start_order_with_late(order: dict, performer_atlas: AtlasApiConnect):
    response = atlas.update_order_state(order["Id"], 'OnItsWay')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': OnItsWay')

    response = performer_atlas.create_eta_for_order(order["Id"], date + 'T20:30:00.000Z')
    if response is not None:
        print('INFO: Created new ETA for order ' + order['OrderInfo']['Number'])

    time.sleep(1)


# 5 Выполняемый заказ на доставку без ETA
def start_order_without_data(order: dict):
    response = atlas.update_order_state(order["Id"], 'OnItsWay')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': OnItsWay')

    time.sleep(1)


# 7 Завершённый заказ на доставку вовремя
def complete_order_in_time(order: dict):
    response = atlas.update_order_state(order["Id"], 'Completed')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Completed')

    response = atlas.create_event_reach_the_client(order["Id"])
    if response is not None:
        print('INFO: New event for order ' + order['OrderInfo']['Number'] + ': ReachedTheClient')

    time.sleep(1)


# 9 Завершённый заказ на доставку с опозданием
def complete_order_with_late(order: dict):
    response = atlas.update_order_state(order["Id"], 'Completed')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Completed')

    response = atlas.create_event_reach_the_client(order["Id"])
    if response is not None:
        print('INFO: New event for order ' + order['OrderInfo']['Number'] + ': ReachedTheClient')

    time.sleep(1)


# 11 Отменённый заказ на доставку
def cancel_order(order: dict):
    response = atlas.update_order_state(order["Id"], 'Cancelled')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Cancelled')

    time.sleep(1)


# 13 Перенесенный заказ на доставку
def pending_order(order: dict):
    response = atlas.update_order_state(order["Id"], 'Pending')
    if response is not None:
        print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Pending')

    time.sleep(1)


def create_data():
    time_slot_from = date + 'T21:00:00.000Z'
    time_slot_to = date + 'T23:00:00.000Z'

    hub_code_1 = '1001'
    hub_code_2 = '119943'

    carrier_id_1 = '976bd44e-7807-4f3b-9e52-38d598758dc0'
    carrier_id_2 = 'b2b9b4ab-7f09-4ad7-8e1a-0ff43c468128'

    performer_id_1 = 'b2a235eb-8335-4fd1-9bed-ad375089f4af'
    performer_id_2 = '76af3fee-908a-4e7e-9a70-aa3c48a00327'

    transport_id_1 = '9b879cda-1b82-429c-85c9-acbe00d62ab5'
    transport_id_2 = 'cf940739-7f2a-4e53-a35d-acbe00d67142'

    # hub_code_1 = '01-01-КЛМ'
    # hub_code_2 = '38030'
    #
    # carrier_id_1 = 'd6b799dc-f464-4919-8435-a7b600cc408a'
    # carrier_id_2 = 'b7173fdc-a379-4cc3-ba72-a7b600ccb1ac'
    #
    # performer_id_1 = '857ef9c7-09a9-4820-b03d-a7c500a34819'
    # performer_id_2 = '29aa7224-9ede-11e8-8d9d-a93b00a1e3ce'
    #
    # transport_id_1 = '14a215ba-7c5e-4214-862f-a7c500a96617'
    # transport_id_2 = '34f9c3ed-e928-4fb4-8432-d96b5d57ef98'

    hubs = atlas.get_all_hubs()

    # if hubs is not None:
    #     for hub in hubs:
    #         if "ExternalId" in hub:
    #             for i in range(0, random.randrange(1, 10)):
    #                 order = create_delivery_order(time_slot_from=time_slot_from,
    #                                               time_slot_to=time_slot_to,
    #                                               hub_code=hub["ExternalId"],
    #                                               carrier_id=carrier_id_1,
    #                                               performer_id=performer_id_1,
    #                                               transport_id=transport_id_1)
    #                 complete_order_in_time(order=order)
    #
    #                 order = create_pickup_order(time_slot_from=time_slot_from,
    #                                             time_slot_to=time_slot_to,
    #                                             hub_code=hub["ExternalId"],
    #                                             carrier_id=carrier_id_1,
    #                                             performer_id=performer_id_1,
    #                                             transport_id=transport_id_1)
    #                 complete_order_in_time(order=order)

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    start_order_in_time(order=order, performer_atlas=performer_atlas_1)

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    start_order_in_time(order=order, performer_atlas=performer_atlas_2)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    start_order_in_time(order=order, performer_atlas=performer_atlas_1)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    start_order_in_time(order=order, performer_atlas=performer_atlas_2)

    print('\n--------- 1 COMPLETED ----------\n')

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    start_order_with_late(order=order, performer_atlas=performer_atlas_1)

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    start_order_with_late(order=order, performer_atlas=performer_atlas_2)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    start_order_with_late(order=order, performer_atlas=performer_atlas_1)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    start_order_with_late(order=order, performer_atlas=performer_atlas_2)
    print('\n--------- 2 COMPLETED ----------\n')

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    start_order_without_data(order=order)

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    start_order_without_data(order=order)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    start_order_without_data(order=order)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    start_order_without_data(order=order)
    print('\n--------- 3 COMPLETED ----------\n')

    order = create_delivery_order(time_slot_from=date + 'T10:00:00.000Z',
                                  time_slot_to=date + 'T23:00:00.000Z',
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    complete_order_in_time(order=order)

    order = create_delivery_order(time_slot_from=date + 'T10:00:00.000Z',
                                  time_slot_to=date + 'T23:00:00.000Z',
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    complete_order_in_time(order=order)

    order = create_pickup_order(time_slot_from=date + 'T10:00:00.000Z',
                                time_slot_to=date + 'T23:00:00.000Z',
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    complete_order_in_time(order=order)

    order = create_pickup_order(time_slot_from=date + 'T10:00:00.000Z',
                                time_slot_to=date + 'T23:00:00.000Z',
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    complete_order_in_time(order=order)
    print('\n--------- 4 COMPLETED ----------\n')

    order = create_delivery_order(time_slot_from=date + 'T10:00:00.000Z',
                                  time_slot_to=date + 'T11:00:00.000Z',
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    complete_order_with_late(order=order)

    order = create_delivery_order(time_slot_from=date + 'T10:00:00.000Z',
                                  time_slot_to=date + 'T11:00:00.000Z',
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    complete_order_with_late(order=order)

    order = create_pickup_order(time_slot_from=date + 'T10:00:00.000Z',
                                time_slot_to=date + 'T11:00:00.000Z',
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    complete_order_with_late(order=order)

    order = create_pickup_order(time_slot_from=date + 'T10:00:00.000Z',
                                time_slot_to=date + 'T11:00:00.000Z',
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    complete_order_with_late(order=order)
    print('\n--------- 5 COMPLETED ----------\n')

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    cancel_order(order=order)

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    cancel_order(order=order)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    cancel_order(order=order)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    cancel_order(order=order)
    print('\n--------- 6 COMPLETED ----------\n')

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_1,
                                  carrier_id=carrier_id_1,
                                  performer_id=performer_id_1,
                                  transport_id=transport_id_1)
    pending_order(order=order)

    order = create_delivery_order(time_slot_from=time_slot_from,
                                  time_slot_to=time_slot_to,
                                  hub_code=hub_code_2,
                                  carrier_id=carrier_id_2,
                                  performer_id=performer_id_2,
                                  transport_id=transport_id_2)
    pending_order(order=order)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_1,
                                carrier_id=carrier_id_1,
                                performer_id=performer_id_1,
                                transport_id=transport_id_1)
    pending_order(order=order)

    order = create_pickup_order(time_slot_from=time_slot_from,
                                time_slot_to=time_slot_to,
                                hub_code=hub_code_2,
                                carrier_id=carrier_id_2,
                                performer_id=performer_id_2,
                                transport_id=transport_id_2)
    pending_order(order=order)
    print('\n--------- 7 COMPLETED ----------\n')


def get_analytics_data():
    response = atlas.get_analytics(date_from=date + 'T00:00:00.000Z', date_to=date + 'T23:59:00.000Z')
    if response is not None:
        print(response)


if __name__ == '__main__':
    try:
        atlas = AtlasApiConnect(url=stand, username=username, password=password)
        performer_atlas_1 = AtlasApiConnect(url=stand, username=performer_username_1, password=performer_password_1)
        performer_atlas_2 = AtlasApiConnect(url=stand, username=performer_username_2, password=performer_password_2)

        atlas.start_client()
        performer_atlas_1.start_client()
        performer_atlas_2.start_client()

        create_data()
        get_analytics_data()

        atlas.stop_client()
        performer_atlas_1.stop_client()
        performer_atlas_2.stop_client()
    except Exception as e:
        print(e)

    '''
    # 2 Выполняемый заказ на возврат вовремя
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'OnItsWay')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': OnItsWay')

        response = carrier_atlas.create_eta_for_order(order["Id"], date + 'T21:30:00.000Z')
        if response is not None:
            print('INFO: Created new ETA for order ' + order['OrderInfo']['Number'])


    # 4 Выполняемый заказ на возврат с опозданием
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'OnItsWay')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': OnItsWay')

        response = carrier_atlas.create_eta_for_order(order["Id"], date + 'T21:30:00.000Z')
        if response is not None:
            print('INFO: Created new ETA for order ' + order['OrderInfo']['Number'])


    # 6 Выполняемый заказ на возврат бeз ETA
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'OnItsWay')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': OnItsWay')


    # 8 Завершённый заказ на возврат вовремя
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'Completed')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Completed')

        response = atlas.create_event_reach_the_client(order["Id"], date + 'T21:50:00.000Z')
        if response is not None:
            print('INFO: New event for order ' + order['OrderInfo']['Number'] + ': ReachedTheClient')


    # 10 Завершённый заказ на возврат с опозданием
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'Completed')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Completed')

        response = atlas.create_event_reach_the_client(order["Id"], date + 'T22:10:00.000Z')
        if response is not None:
            print('INFO: New event for order ' + order['OrderInfo']['Number'] + ': ReachedTheClient')


    # 12 Отменённый заказ на возврат
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'Cancelled')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Cancelled')


    # 14 Перенесенный заказ на возврат
    order = atlas.create_pickup_order(order_number='AnalyticsTest_' + str(random.randrange(10000)),
                                      hub_code=hub_code,
                                      carrier_code=carrie_code,
                                      transport_number=transport_number,
                                      pickup_from=time_slot_from,
                                      pickup_to=time_slot_to,
                                      longitude=longitude,
                                      latitude=latitude)

    if order is not None:
        print('INFO: Created new order ' + order['OrderInfo']['Number'] + ' with id: ' + order["Id"])

        time.sleep(5)
        response = atlas.update_order_state(order["Id"], 'Pending')
        if response is not None:
            print('INFO: New status for order ' + order['OrderInfo']['Number'] + ': Pending')
    '''
