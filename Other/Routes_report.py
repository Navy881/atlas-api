
import datetime
from AtlasApi import AtlasApiConnect

url = ""
username = ""
password = ""


def route_report():
    routes = atlas.get_routes()

    print(f'Всего маршрутов: {len(routes["value"])}\n')

    print("№;Дата маршрута;Маршрут;Вес груза, кг.;Мин. требуемая грузоподъемность ТС, кг.;"
          "Макс. требуемая грузоподъемность ТС, кг.;Требуемая грузоподъемность ТС, кг.;Назначенное ТС;"
          "Грузоподъемность ТС, кг;Недозагруженность ТС, кг.")

    j = 0
    for i, route in enumerate(routes['value']):
        if route['HubInfo']['HubId'] == '4b5de9c1-3117-4f57-996d-a9a600bcd4c8':

            route = atlas.get_route(route_id=route['Id'])

            if "RoutePoints" not in route or "PerformerInfo" not in route or "TransportRestrictionsInfo" not in route:
                continue

            if "TypedRestrictions" not in route["TransportRestrictionsInfo"]:
                continue

            route_start = route["RouteInfo"]["Start"].split('T')[0]
            route_name = route["RouteInfo"]["Name"]
            route_weight = -1
            need_weight = route["TransportRestrictionsInfo"]["TypedRestrictions"][0]["Value"]
            min_weight = 0
            max_weight = 0

            for route_point in route['RoutePoints']:
                if route_point['RoutePointInfo']['PointType'] == "Delivery":
                    for order_task in route_point['OrderTasks']:
                        order = atlas.get_order_by_id(order_id=order_task['OrderId'])
                        if order is not None:
                            for product in order['Products']:
                                route_weight += product['Weight'] * product['Quantity']

                            if order['TransportRestrictionsInfo']['TypedRestrictions'][0]['Value']['MinWeight'] < min_weight:
                                min_weight = order['TransportRestrictionsInfo']['TypedRestrictions'][0]['Value']['MinWeight']

                            if order['TransportRestrictionsInfo']['TypedRestrictions'][0]['Value']['MaxWeight'] > max_weight:
                                max_weight = order['TransportRestrictionsInfo']['TypedRestrictions'][0]['Value']['MaxWeight']

            transport = atlas.get_transport(transport_id=route['PerformerInfo']['TransportId'])
            transport_number = transport["Number"]
            transport_weight = transport["WeightType"]

            if route_weight > -1:
                j += 1
                print(f'{j};{route_start};{route_name};{int(route_weight) + 1};{min_weight};{max_weight};{need_weight};'
                      f'{transport_number};{transport_weight};{transport_weight - int(route_weight)}')


if __name__ == '__main__':
    try:
        atlas = AtlasApiConnect(url=url, username=username, password=password)
        atlas.start_client()

        route_report()

        atlas.stop_client()
    except Exception as e:
        print(e)
