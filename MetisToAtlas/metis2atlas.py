import json
import time
from datetime import datetime, timedelta

from AtlasApi import AtlasApiConnect

ORDERS_FILE = 'metis-real-verniy.json'
ROUTES_FILE = 'metis-real-verniy-zoned-oldzones-nc.json'
HUB_LATITUDE = 55.733996
HUB_LONGITUDE = 37.588473
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DAYS_SHIFT = 40
TIME_OFFSET = 3

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)


def read_json_file(file):
    with open(file, 'r', encoding="utf8") as f:
        data = json.loads(f.read())
    return data


def date_shift(datetime_str, days, hours=3):
    datetime_str = datetime_str.split('Z')[0].split('.')[0]
    datetime_obj = datetime.strptime(datetime_str, DATETIME_FORMAT)
    datetime_obj = datetime_obj + timedelta(days=days, hours=hours)
    datetime_str_o = datetime_obj.strftime(DATETIME_FORMAT)
    return datetime_str_o


def get_order(orders_data, order_id):
    result = None
    for elem in orders_data:
        if elem['id'] == order_id:
            result = elem
    return result


if __name__ == '__main__':
    try:
        orders = read_json_file(ORDERS_FILE)
        orders = orders['tasks'][0]['orders']
        routes = read_json_file(ROUTES_FILE)
        routes = routes['tasks']['verniy']['routes']

        atlas.start_client()
        '''
        start_time = time.time()
        n = 0
        for order in orders:
            if order['orderType'] == 'Delivery':
                order_names = order['id'].split('-')
                for i in range(0, len(order_names)-1):
                    order_number = order_names[i] + '-delivery' + '+' + str(DAYS_SHIFT) + '_days'
                    order_delivery_time_from = date_shift(order['timeInterval']['start'], DAYS_SHIFT, TIME_OFFSET)
                    order_delivery_time_to = date_shift(order['timeInterval']['end'], DAYS_SHIFT, TIME_OFFSET)
                    order_latitude = order['location']['latitude']
                    order_longitude = order['location']['longitude']

                    response = atlas.get_order_by_external_id(order_external_id=order_number)
                    n += 1
                    print(n)
                    if response is None:
                        print(n, order_number)
                        atlas.create_delivery_order(order_number=order_number,
                                                    op_type='Delivery',
                                                    delivery_from=order_delivery_time_from,
                                                    delivery_to=order_delivery_time_to,
                                                    latitude=order_latitude,
                                                    longitude=order_longitude)
                        time.sleep(0.1)

            elif order['orderType'] == 'Pickup':
                order_names = order['id'].split('-')
                for i in range(0, len(order_names)-1):
                    order_number = order_names[i] + '-pickup' + '+' + str(DAYS_SHIFT) + '_days'
                    order_pickup_time_from = date_shift(order['timeInterval']['start'], DAYS_SHIFT, TIME_OFFSET)
                    order_pickup_time_to = date_shift(order['timeInterval']['end'], DAYS_SHIFT, TIME_OFFSET)
                    order_latitude = order['location']['latitude']
                    order_longitude = order['location']['longitude']

                    response = atlas.get_order_by_external_id(order_external_id=order_number)
                    n += 1
                    print(n)
                    if response is None:
                        print(n, order_number)
                        atlas.create_pickup_order(order_number=order_number,
                                                  op_type='PickUp',
                                                  pickup_from=order_pickup_time_from,
                                                  pickup_to=order_pickup_time_to,
                                                  latitude=order_latitude,
                                                  longitude=order_longitude)

                        # time.sleep(0.1)

        print("--- %s seconds ---" % (time.time() - start_time))
        input('Continue...')
        '''
        start_time = time.time()
        n = 1
        for route in routes:
            route_name = route['vehicleId'] + '+' + str(DAYS_SHIFT) + '_days'
            print(n, route_name)
            route_start = date_shift(route['departureTime'], DAYS_SHIFT, TIME_OFFSET)
            route_end = date_shift(route['arrivalTime'], DAYS_SHIFT, TIME_OFFSET)
            route_model = atlas.get_route_by_external_id(route_external_id=route_name)
            if route_model is None:
                route_body = {}
                route_info = {"Name": route['vehicleId'] + '+' + str(DAYS_SHIFT) + '_days',
                              "Start": date_shift(route['departureTime'], DAYS_SHIFT, TIME_OFFSET),
                              "End": date_shift(route['arrivalTime'], DAYS_SHIFT, TIME_OFFSET),
                              "ExternalId": route['vehicleId'] + '+' + str(DAYS_SHIFT) + '_days'}
                route_body["RouteInfo"] = route_info

                old_point_type = ''
                m = 0
                route_points = []
                point_body = {}
                order_tasks = []

                for point in route['legs']:
                    if point['legType'] == 'OrderPickup' or point['legType'] == 'Order':
                        if point['legType'] == 'OrderPickup':
                            if old_point_type != 'OrderPickup':
                                point_body = {}
                                order_tasks = []
                                old_point_type = 'OrderPickup'
                                planning_time = date_shift(point['arrivalTime'], DAYS_SHIFT, TIME_OFFSET)
                                point_latitude = HUB_LATITUDE
                                point_longitude = HUB_LONGITUDE

                                point_body["LocationInfo"] = {"Longitude": point_longitude, "Latitude": point_latitude}
                                point_body["PlanningInfo"] = {"PlanningTime": planning_time}
                                point_body["RoutePointInfo"] = {"PointType": "PickUp"}
                                point_body["OrderingInfo"] = {"Order": m}
                                m += 1

                                order_names = point['orderId'].split('-')
                                for i in range(0, len(order_names) - 1):
                                    order_name = order_names[i] + '-pickup' + '+' + str(DAYS_SHIFT) + '_days'
                                    order_model = atlas.get_order_by_external_id(order_external_id=order_name)
                                    order_id = order_model['Id']
                                    order_task_body = {"OrderId": order_id}
                                    order_tasks.append(order_task_body)

                            else:
                                order_names = point['orderId'].split('-')
                                for i in range(0, len(order_names) - 1):
                                    order_name = order_names[i] + '-pickup' + '+' + str(DAYS_SHIFT) + '_days'
                                    order_model = atlas.get_order_by_external_id(order_external_id=order_name)
                                    order_id = order_model['Id']
                                    order_task_body = {"OrderId": order_id}
                                    order_tasks.append(order_task_body)

                        elif point['legType'] == 'Order':
                            if old_point_type != 'Order':
                                point_body["OrderTasks"] = order_tasks
                                route_points.append(point_body)

                            point_body = {}
                            order_tasks = []
                            old_point_type = 'Order'

                            planning_time = date_shift(point['arrivalTime'], DAYS_SHIFT, TIME_OFFSET)
                            order_model = get_order(orders, point['orderId'])
                            point_latitude = order_model['location']['latitude']
                            point_longitude = order_model['location']['longitude']

                            point_body["LocationInfo"] = {"Longitude": point_longitude, "Latitude": point_latitude}
                            point_body["PlanningInfo"] = {"PlanningTime": planning_time}
                            point_body["RoutePointInfo"] = {"PointType": "Delivery"}
                            point_body["OrderingInfo"] = {"Order": m}
                            m += 1

                            order_names = point['orderId'].split('-')
                            for i in range(0, len(order_names) - 1):
                                order_name = order_names[i] + '-delivery' + '+' + str(DAYS_SHIFT) + '_days'
                                order_model = atlas.get_order_by_external_id(order_external_id=order_name)
                                order_id = order_model['Id']
                                order_task_body = {"OrderId": order_id}
                                order_tasks.append(order_task_body)

                            point_body["OrderTasks"] = order_tasks
                            route_points.append(point_body)

                route_body["RoutePoints"] = route_points
                atlas.create_route_from_json(body_json=route_body)
            # else:
            #     route_id = route_model['Id']
            #     print(n, 'Moving', route_model['RouteInfo']['Name'])
            #     atlas.move_route(route_id=route_id)
            n += 1
            # input('Ok....')
        print("--- %s seconds ---" % (time.time() - start_time))

    except Exception as e:
        print(e)
