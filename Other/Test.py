
import datetime
from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''


def test_tactical_leg_api():
    atlas = AtlasApiConnect(url=stand, username=username, password=password)
    atlas.start_client()
    carrier_ids = ['9e94a66e-62bd-4fb9-b279-a7b600cbcebe']
    order_ids = []
    order_col = 3
    products = [{'Name': '6000', 'Article': '6000', 'Quantity': 3, 'Weight': 2000},
                {'Name': '9990', 'Article': '9990', 'Quantity': 30, 'Weight': 333},
                {'Name': '15000', 'Article': '15000', 'Quantity': 1000, 'Weight': 15}]

    input('Press to continue 1...')
    leg = atlas.create_leg(leg_external_id='QueueTest_52', stat_point_name='Коломна',
                           end_point_name='Мск. Обл. Зона 52')

    input('Press to continue 2...')
    if leg is not None:
        atlas.create_contract_for_leg(leg_id=leg['Id'], weight_type=5000, carrier_id=carrier_ids[0], ts_count=1)

        input('Press to continue 3...')
        for i in range(order_col):
            order = create_order(atlas, leg_external_id=leg['ExternalId'], products=products[i])
            if order is not None:
                order_ids.append(order['Id'])

    input('Press to continue 4...')
    route = atlas.get_route_by_order_id(order_id=order_ids[0])
    if route is not None:
        atlas.auto_assign(route_id=route[0]['Id'])

    input('Press to continue 5...')
    atlas.create_contract_for_leg(leg_id=leg['Id'], weight_type=10000, carrier_id=carrier_ids[0], ts_count=1)

    input('Press to continue 6...')
    if route is not None:
        atlas.auto_assign(route_id=route[0]['Id'])

    input('Press to continue 7...')
    route = atlas.get_route_by_order_id(order_id=order_ids[1])
    if route is not None:
        atlas.auto_assign(route_id=route[0]['Id'])

    input('Press to continue 8...')
    atlas.create_contract_for_leg(leg_id=leg['Id'], weight_type=20000, carrier_id=carrier_ids[0], ts_count=2)

    input('Press to continue 9...')
    route = atlas.get_route_by_order_id(order_id=order_ids[2])
    if route is not None:
        atlas.auto_assign(route_id=route[0]['Id'])

    input('Press to continue 10...')


def create_order(AtlasApiConnect, leg_external_id, products):
    order_number = 'OTBG-' + str(datetime.datetime.now())
    method_url = 'oms/api/Orders'
    headers = {'Authorization': 'Bearer ' + AtlasApiConnect.get_user_token(),
               'Content-Type': 'application/json; charset=utf-8'}
    body = {
                "OrderInfo": {
                    "ExternalId": order_number,
                    "Number": order_number,
                    "OperationType": "Delivery"
                },
                "AllocationInfo": {
                    "HubCode": "01-01-КЛМ",
                    "RouteExternalId": "",
                    "CarrierCode": "",
                    "TacticalLegExternalId": leg_external_id
                },
                "DeliveryTimeSlot": {
                    "From": "2019-11-10T15:00:00.000Z",
                    "To": "2019-11-10T17:00:00.000Z"
                },
                "ContactInfo": {
                    "Name": "Иванов Иван Иванович",
                    "Phones": [
                        "+79999999999"
                    ]
                },
                "AddressInfo": {
                    "FullAddress": "Lingnerallee, 3, Dresden, Germany. 01069",
                    "Country": "Germany",
                    "PostalCode": "01069",
                    "District": "Dresden",
                    "Town": "Dresden",
                    "TownRegion": "Altstadt",
                    "Street": "Lingnerallee",
                    "Building": "3",
                    "Region": "Sachsen"
                },
                "LocationInfo": {
                    "Longitude": 39.643191,
                    "Latitude": 47.261389
                },
                "TransportRestrictionsInfo": {
                    "LoadUnloadTypes": [
                        "BothSide"
                    ],
                    "TransportRestrictions": ["34351"]
                },
                "Products": [
                    {
                        "Name": products["Name"],
                        "Article": products["Article"],
                        "Quantity": products["Quantity"],
                        "Weight": products["Weight"]
                    }
                ]
            }
    response = AtlasApiConnect.request(method_url=method_url, method_type='post', headers=headers, body=body)
    if response is not None:
        print('\nOrder created')
        print(response)
    else:
        print('\nOrder creating failed')
    return response


if __name__ == '__main__':
    try:
        test_tactical_leg_api()

        # atlas = AtlasApiConnect(stand=stand, domain=domain, username=username, password=password)
        # atlas.start_client()
        # products = [{'Name': '6000', 'Article': '6000', 'Quantity': 3, 'Weight': 2000},
        #             {'Name': '9990', 'Article': '9990', 'Quantity': 30, 'Weight': 333},
        #             {'Name': '15000', 'Article': '15000', 'Quantity': 1000, 'Weight': 15}]
        #
        # create_order(atlas, 'QueueTest_21', products[0])
    except Exception as e:
        print(e)
