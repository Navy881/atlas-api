# -*- coding: utf-8 -*-
import datetime
import random

import requests
import time
import json

success_status_code = [200, 201]

company_url = ''
username = ''
password = ''

TACTICAL_LEG_ID = ''
TACTICAL_LEG_EXTERNAL_ID = 'QueueTest_28'


def get_sessionId(username, password):
    url = company_url + 'auth/api/v1/Login'
    r = requests.post(url, json={"username": username, "password": password})
    print('\n' + r.url)
    data = r.json()
    if 'sessionId' in data:
        print('SessionId Ok: ' + data['sessionId'])
        return 'Ok', data['sessionId']
    else:
        print('SessionId error: ' + data['message'])
        return 'SessionId error.', data['message']


def get_token():
    status, message = get_sessionId(username, password)
    if status == 'Ok':
        sessionId = message
        params = {'sessionId': sessionId}
        url = company_url + 'auth/api/v1/Token/sessionId'
        r = requests.post(url, params=params)
        print('\n' + r.url)
        data = r.json()
        if 'token' in data:
            print('Token Ok: ' + data['token'])
            return 'Ok', data['token']
        else:
            return 'Token error.', data['message']
    else:
        return status, message


def create_order(token):
    order_number = 'OTBG-' + str(datetime.datetime.now())
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json; charset=utf-8'}
    data = {
              "OrderInfo": {
                "ExternalId": order_number,
                "Number": order_number,
                "OperationType": "Delivery"
              },
              "AllocationInfo": {
                "HubCode": "01-01-КЛМ",
                "RouteExternalId": "",
                "CarrierCode": "",
                "TacticalLegExternalId": TACTICAL_LEG_EXTERNAL_ID
              },
              "DeliveryTimeSlot": {
                "From": "2019-11-15T15:00:00.000Z",
                "To": "2019-11-15T17:00:00.000Z"
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
               }
            }
    url = company_url + 'oms/api/Orders'
    r = requests.post(url, headers=headers, data=json.dumps(data))
    if r.status_code in success_status_code:
        data = r.json()
        message = data
    else:
        message = 'Error'
    return r.status_code, message


def get_route_by_order(token, order_id):
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json; charset=utf-8'}
    url = company_url + 'tms/api/Orders/' + order_id + '/Routes'
    r = requests.get(url, headers=headers)
    if r.status_code in success_status_code:
        data = r.json()
        message = data
    else:
        message = 'Error'
    return r.status_code, message


def set_tactical_leg_info_for_route(token, route_id, tactical_leg_id):
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json; charset=utf-8'}
    data = {
        "TacticalLegId": tactical_leg_id
    }
    url = company_url + 'tms/api/Routes/' + route_id + '/TacticalLegInfo'
    r = requests.put(url, headers=headers, data=json.dumps(data))
    if r.status_code in success_status_code:
        data = r.json()
        message = data
    else:
        message = 'Error'
    return r.status_code, message


def main(order_col=1):
    orders_id = []
    status, message = get_token()
    if status == "Ok":
        print('\n')
        token = message
        for i in range(order_col):
            status, message = create_order(token)
            # print(status)
            if status in success_status_code:
                order = message
                orders_id.append(order['Id'])
                print(order['Id'], order['OrderInfo']['Number'])

        time.sleep(3)

        for order_id in orders_id:
            status, message = get_route_by_order(token, order_id)
            # print(status)
            if status in success_status_code:
                route = message
                print(route[0]['Id'], route[0]['RouteInfo']['Name'])
                    
    input('Press any key...')


if __name__ == '__main__':
    try:
        order_col = int(input('Orders col: '))
        main(order_col)
    except Exception as e:
        print(e)
