import json
import time
from datetime import datetime, timedelta


ORDERS_FILE = 'metis-real-verniy-2-1-zoned.json'
ROUTES_FILE = 'решение-4-рейса-малые-опоздания-без-зон.json'
# ROUTES_FILE = 'решение-3-рейса-малые-опоздания-ещё-10-5тонных.json'
# ROUTES_FILE = 'решение-зоны-большие-опоздания-3-рейса.json'
# ROUTES_FILE = 'metis-real-verniy-zoned-oldzones-nc.json'
# ROUTES_FILE = 'metis-real-verniy-my-osrm-41808-30-to-30.json'
# ROUTES_FILE = 'metis-real-zoned-large-cars-41800-result.json'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
TIME_OFFSET = 3


def read_json_file(file):
    with open(file, 'r', encoding="utf8") as f:
        data = json.loads(f.read())
    return data


def date_shift(datetime_str, days):
    datetime_str = datetime_str.split('Z')[0].split('.')[0]
    datetime_obj = datetime.strptime(datetime_str, DATETIME_FORMAT)
    datetime_obj = datetime_obj + timedelta(days=days)
    datetime_str_o = datetime_obj.strftime(DATETIME_FORMAT)
    return datetime_str_o


def str2datetime(datetime_str, time_offset):
    datetime_str = datetime_str.split('Z')[0].split('.')[0]
    datetime_obj = datetime.strptime(datetime_str, DATETIME_FORMAT)
    datetime_obj = datetime_obj + timedelta(hours=time_offset)
    return datetime_obj


def datetime2hm(datetime_obj):
    parts = str(datetime_obj).split(' ')[1].split(':')
    datetime_str = parts[0] + ':' + parts[1]
    return datetime_str


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

        total_duration = datetime.now() - datetime.now()
        total_travel_time = datetime.now() - datetime.now()
        total_waiting_time = datetime.now() - datetime.now()
        max_duration = datetime.now() - datetime.now()
        total_hub_to_hub_count = 0
        routes_count = 0
        total_late_time = datetime.now() - datetime.now()
        max_late_time = datetime.now() - datetime.now()

        for route in routes:
            if True:  # route['vehicleId'] == 'VOLVO M507TA62':
                routes_count += 1
                print("Маршрут {}: {}\n".format(routes_count, route['vehicleId']))
                legs = route['legs']
                old_point_type = ''
                f_point_start = datetime.now()
                f_point_end = datetime.now()
                s_point_start = datetime.now()
                s_point_end = datetime.now()
                i = 0
                load_count = 0
                route_duration = datetime.now() - datetime.now()
                load_weight = 0
                load_volume = 0
                load_order_numbers = ''
                delivery_order_numbers = ''
                hub_to_hub_count = 0
                route_late_time = datetime.now() - datetime.now()

                for n, leg in enumerate(legs):
                    if leg['legType'] == 'OrderPickup':
                        order = get_order(orders, leg['orderId'])
                        for p in range(0, len(leg['orderId'].split('-'))-1):
                            load_order_numbers += str(leg['orderId'].split('-')[p]) + ' '
                        load_weight += order['constraints']['dimensionConstraints'][0]['value']
                        load_volume += order['constraints']['dimensionConstraints'][1]['value']
                        if old_point_type != 'OrderPickup':
                            f_point_start = str2datetime(leg['arrivalTime'], TIME_OFFSET)
                            f_point_end = str2datetime(leg['departureTime'], TIME_OFFSET)
                            if old_point_type == 'Order':
                                print("... В пути: {}".format(f_point_start - s_point_end))
                                route_duration += (f_point_start - s_point_end)
                                total_travel_time += (f_point_start - s_point_end)
                        else:
                            f_point_end = str2datetime(leg['departureTime'], TIME_OFFSET)
                        old_point_type = 'OrderPickup'

                    elif leg['legType'] == 'Order':
                        order = get_order(orders, leg['orderId'])
                        for p in range(0, len(leg['orderId'].split('-'))-1):
                            delivery_order_numbers += str(leg['orderId'].split('-')[p]) + ' '
                        s_point_start = str2datetime(leg['arrivalTime'], TIME_OFFSET)
                        if old_point_type == 'Order':
                            print("... В пути: {}".format(s_point_start - s_point_end))
                            route_duration += (s_point_start - s_point_end)
                            total_travel_time += (s_point_start - s_point_end)

                        s_point_end = str2datetime(leg['departureTime'], TIME_OFFSET)

                        i += 1
                        if i == 1:
                            # s_point_start = str2datetime(order['timeInterval']['start'], TIME_OFFSET)
                            load_duration = f_point_end - f_point_start
                            f_point_end = s_point_start - (str2datetime(leg['arrivalTime'], TIME_OFFSET) - f_point_end)
                            f_point_start = f_point_end - load_duration

                        if old_point_type == 'OrderPickup' and i == 1:
                            load_count += 1
                            print("🏠 Выезд со склада {}: {} (вес: {} кг, объём: {} м3)".format(load_count,
                                                                                                datetime2hm(f_point_end),
                                                                                                load_weight,
                                                                                                load_volume))
                            print("   Заказы: {}".format(load_order_numbers))
                            load_weight = 0
                            load_volume = 0
                            load_order_numbers = ''
                            hub_to_hub_count += 1

                        if old_point_type == 'OrderPickup':
                            if i > 1:
                                load_count += 1
                                print("🏠 Погрузка на складе {}: {} - {} (длительность: {}, "
                                      "вес: {} кг, объём: {} м3)".format(load_count,
                                                                         datetime2hm(f_point_start),
                                                                         datetime2hm(f_point_end),
                                                                         f_point_end - f_point_start,
                                                                         load_weight,
                                                                         load_volume))
                                route_duration += (f_point_end - f_point_start)
                                load_weight = 0
                                load_volume = 0
                                print("   Заказы: {}".format(load_order_numbers))
                                load_order_numbers = ''
                                hub_to_hub_count += 1

                                print("... В пути: {}".format(s_point_start - f_point_end))
                                route_duration += (s_point_start - f_point_end)
                                total_travel_time += (s_point_start - f_point_end)
                            else:
                                print("... В пути: {}".format(s_point_start - f_point_end))
                                route_duration += (s_point_start - f_point_end)
                                total_travel_time += (s_point_start - f_point_end)

                        if str2datetime(leg['arrivalTime'], TIME_OFFSET) < \
                                str2datetime(order['timeInterval']['start'], TIME_OFFSET): # and i > 1:
                            # s_point_start = str2datetime(order['timeInterval']['start'], TIME_OFFSET)
                            s_point_start = s_point_end - timedelta(milliseconds=order['serviceTime'])
                            if (s_point_start - str2datetime(leg['arrivalTime'], TIME_OFFSET)).seconds > 1 and i > 1:
                                print("⌛ Ожидание: {}".format(s_point_start - str2datetime(leg['arrivalTime'], TIME_OFFSET)))
                                route_duration += (s_point_start - str2datetime(leg['arrivalTime'], TIME_OFFSET))
                                total_waiting_time += (s_point_start - str2datetime(leg['arrivalTime'], TIME_OFFSET))

                        late_time = datetime.now() - datetime.now()
                        if s_point_start > str2datetime(order['timeInterval']['end'], TIME_OFFSET):
                            late_time = s_point_start - str2datetime(order['timeInterval']['end'], TIME_OFFSET)
                            if max_late_time < late_time:
                                max_late_time = late_time
                        route_late_time += late_time

                        print("↑ Выгрузка {}: {} - {} (длительность: {}, период доставки: {}-{}, опоздание: {}, "
                              "вес: {} кг, "
                              "объём: {} м3)".format(i,
                                                     datetime2hm(s_point_start),
                                                     datetime2hm(s_point_end),
                                                     s_point_end - s_point_start,
                                                     datetime2hm(str2datetime(order['timeInterval']['start'], TIME_OFFSET)),
                                                     datetime2hm(str2datetime(order['timeInterval']['end'], TIME_OFFSET)),
                                                     late_time,
                                                     order['constraints']['dimensionConstraints'][0]['value'],
                                                     order['constraints']['dimensionConstraints'][1]['value']))
                        route_duration += (s_point_end - s_point_start)
                        old_point_type = 'Order'
                        print("   Заказы: {}".format(delivery_order_numbers))
                        delivery_order_numbers = ''

                    elif leg['legType'] == 'End':
                        f_point_start = str2datetime(leg['arrivalTime'], TIME_OFFSET)
                        print("... В пути: {}".format(f_point_start - s_point_end))
                        route_duration += (f_point_start - s_point_end)
                        total_travel_time += (f_point_start - s_point_end)

                        print("🏁 Возвращение на склад: {}\n".format(datetime2hm(f_point_start)))
                        print("Количество рейсов в маршруте: {}".format(hub_to_hub_count))
                        print("Общая длительность: {}".format(route_duration))
                        print("Суммарное опоздание: {}\n".format(route_late_time))
                        total_duration += route_duration
                        total_hub_to_hub_count += hub_to_hub_count
                        total_late_time += route_late_time
                        if route_duration > max_duration:
                            max_duration = route_duration

            print('========================================================')
        print("\nОбщее количество рейсов: {}".format(total_hub_to_hub_count))
        print("Общая длительность маршрутов, ч: {}".format(total_duration.total_seconds()/3660))
        print("Общее время в пути, ч: {}".format(total_travel_time.total_seconds()/3660))
        print("Общее время ожидания, ч: {}".format(total_waiting_time.total_seconds()/3660))
        print("Max длительность маршрута: {}".format(max_duration))
        print("Max опоздание: {}".format(max_late_time))
        print("Среднее время в пути на всём маршруте, ч: {}".format(total_duration.total_seconds()/3660/len(routes)))
        print("Среднее время в пути на рейсе, ч: {}".format(total_duration.total_seconds()/3660/total_hub_to_hub_count))
        print("Среднее время ожидания на всём маршруте, ч: {}".format(total_waiting_time.total_seconds()/3660/len(routes)))
        print("Среднее время ожидания на рейсе, ч: {}".format(total_waiting_time.total_seconds()/3660/total_hub_to_hub_count))
        print("Среднее время опоздания, ч: {}".format(total_late_time.total_seconds()/3660/len(routes)))

    except Exception as e:
        print(e)
