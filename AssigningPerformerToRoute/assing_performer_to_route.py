# -*- coding: utf-8 -*-

import json
import time
import requests
from datetime import datetime


class AtlasApiConnect(object):

    def __init__(self, url='https://dev3.cargoonline.ru/', moloch_url=None, username=None, password=None):
        self.url = url
        self.moloch_url = moloch_url
        self.username = username
        self.password = password
        self.success_status_code = [200, 201]
        self.unauthorized_status_code = [401]
        self.user_session_id = ''
        self.user_token = ''
        self.user_connection_id = ''

    def __del__(self):
        self.__logout()

    def get_url(self):
        return self.url

    def get_user_token(self):
        return self.user_token

    def get_user_connection_id(self):
        return self.user_connection_id

    def request(self, method_url, method_type, params=None, headers=None, body=None):
        response = ''
        if method_type == 'get':
            response = self.__get(self.url+method_url, params, headers)
        elif method_type == 'post':
            response = self.__post(self.url+method_url, params, headers, body)
        elif method_type == 'put':
            response = self.__put(self.url+method_url, params, headers, body)
        elif method_type == 'delete':
            response = self.__delete(self.url+method_url, params, headers, body)
        return response

    def __get(self, url, params=None, headers=None):
        result = None
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                result = response.json()
                if 'Message' in result:
                    if result['Message'] == 'Unauthorized':
                        self.start_client()
                        time.sleep(2)
                        self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __post(self, url, params=None, headers=None, body=None):
        result = None
        try:
            response = requests.post(url, params=params, headers=headers, json=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                result = response.json()
                if 'Message' in result:
                    if result['Message'] == 'Unauthorized':
                        self.start_client()
                        time.sleep(2)
                        self.__post(url, params, headers, body)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __put(self, url, params=None, headers=None, body=None):
        result = None
        try:
            response = requests.put(url, params=params, headers=headers, data=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                result = response.json()
                if 'Message' in result:
                    if result['Message'] == 'Unauthorized':
                        self.start_client()
                        time.sleep(2)
                        self.__put(url, params, headers, body)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __delete(self, url, params=None, headers=None, body=None):
        result = None
        try:
            response = requests.delete(url, params=params, headers=headers, data=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                result = response.json()
                if 'Message' in result:
                    if result['Message'] == 'Unauthorized':
                        self.start_client()
                        time.sleep(2)
                        self.__delete(url, params, headers, body)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __get_session_id(self):
        method_url = 'auth/api/v1/Login'
        body = {"username": self.username, "password": self.password}
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is not None and 'sessionId' in response:
            self.user_session_id = response['sessionId']
            print('INFO: ' + str(datetime.now()) + ' ' + self.url + ' session Id: ' + self.user_session_id)

    def __get_token(self):
        method_url = 'auth/api/v1/Token/sessionId'
        params = {'sessionId': self.user_session_id}
        response = self.request(method_url=method_url, method_type='post', params=params)
        if response is not None and 'token' in response:
            self.user_token = response['token']
            print('INFO: ' + str(datetime.now()) + ' ' + self.url + ' Token: ' + self.user_token)

    def __get_connection_id(self):
        method_url = 'notify/api/signalr/negotiate'
        params = {'AUTH_TOKEN': self.user_token}
        response = self.request(method_url=method_url, method_type='post', params=params)
        if response is not None and 'connectionId' in response:
            self.user_connection_id = response['connectionId']
            print('INFO: ' + str(datetime.now()) + ' ' + self.url + ' Connection Id: ' + self.user_connection_id)

    def __logout(self):
        method_url = 'auth/api/v1/Logout/' + self.user_session_id
        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        response = self.request(method_url=method_url, method_type='post', headers=headers)
        if response is not None:
            print('INFO: ' + str(datetime.now()) + ' Atlas connection ' + self.url + ' closed')

    def start_client(self):
        print('INFO: ' + str(datetime.now()) + ' Atlas connection ' + self.url + ' connects')
        self.__get_session_id()
        if self.user_session_id != '':
            self.__get_token()
        if self.user_token != '':
            self.__get_connection_id()

    def stop_client(self):
        self.__del__()

    def get_routes_in_state(self, route_state='CarrierAssigned'):
        method_url = 'tms/api/odata/route'
        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        params = {'$count': 'true',
                  '$expand': "RoutePoints,RoutePoints($expand=OrderTasks),StateInfo($select=State)",
                  '$filter': "StateInfo/State eq '" + route_state + "'",
                  '$select': 'Id'}
        response = self.request(method_url=method_url, method_type='get', headers=headers, params=params)
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    def get_order_by_id(self, order_id):
        method_url = 'oms/api/Orders/' + order_id
        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        response = self.request(method_url=method_url, method_type='get', headers=headers)
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    def get_all_transport(self):
        method_url = 'resources/api/transports'
        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        response = self.request(method_url=method_url, method_type='get', headers=headers)
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    def update_route_performer_info(self, route_id, transport_id, person_id):
        method_url = 'tms/api/Routes/' + route_id + '/PerformerInfo'
        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        body = {
            "TransportId": transport_id,
            "PersonIds": [person_id]
        }
        response = self.request(method_url=method_url, method_type='put', headers=headers, body=json.dumps(body))
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response

    def set_route_state(self, route_id, route_state):
        method_url = 'tms/api/Routes/' + route_id + '/StateInfo'
        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        body = {
            "State": route_state
        }
        response = self.request(method_url=method_url, method_type='put', headers=headers, body=json.dumps(body))
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response


TOTAL_PERIOD_IN_SEC = 43200  # 12 hours
CHECK_PERIOD_IN_SEC = 10
TRIGGER_ROUTE_STATE = 'CarrierAssigned'
TARGET_ROUTE_STATE = 'PerformerAssigned'
TRANSPORTS = []

stand = ''
username = ''
password = ''

atlas = AtlasApiConnect(url=stand, username=username, password=password)


def assign_performer_to_route(route_id, transport_number):
    if TRANSPORTS is not None:
        for transport in TRANSPORTS:
            if 'Number' in transport:
                if transport['Number'].lower() == transport_number.lower():
                    transport_id = transport['Id']
                    if 'PreferredPersons' in transport:
                        if len(transport['PreferredPersons']) > 0:
                            person_id = transport['PreferredPersons'][0]['PersonId']
                            request = atlas.update_route_performer_info(route_id=route_id,
                                                                        transport_id=transport_id,
                                                                        person_id=person_id)

                            print('INFO: ' + str(datetime.now()) + ' Transport: ' + transport_number.lower() +
                                  ' assigned to Route: ' + route_id)
                            if request is not None:
                                atlas.set_route_state(route_id=route_id, route_state=TARGET_ROUTE_STATE)
                            break


def search_routes():
    routes = atlas.get_routes_in_state(route_state=TRIGGER_ROUTE_STATE)
    if routes is not None:
        if 'value' in routes:
            routes = routes['value']
            print('INFO: ' + str(datetime.now()) + ' ' + str(len(routes)) + ' routes found')
            if len(routes) > 0:

                for route in routes:
                    if 'StateInfo' in route and 'RoutePoints' in route:
                        if route['StateInfo']['State'] == TRIGGER_ROUTE_STATE:
                            route_points = route['RoutePoints']
                            if len(route_points) > 0:
                                if 'OrderTasks' in route_points[0]:
                                    orders_tasks = route_points[0]['OrderTasks']
                                    if len(orders_tasks) > 0:
                                        order_id = orders_tasks[0]['OrderId']
                                        order = atlas.get_order_by_id(order_id=order_id)
                                        if order is not None:
                                            if 'Comments' in order:
                                                if len(order['Comments']) > 0:
                                                    transport_number = order['Comments'][0]['Comment']
                                                    assign_performer_to_route(route_id=route['Id'],
                                                                              transport_number=transport_number)


if __name__ == '__main__':
    try:
        start_time = time.time()
        check_time = start_time
        atlas.start_client()
        TRANSPORTS = atlas.get_all_transport()
        search_routes()
        while True:
            if time.time() - check_time >= CHECK_PERIOD_IN_SEC:
                search_routes()
                check_time = time.time()
            elif time.time() - start_time > TOTAL_PERIOD_IN_SEC:
                atlas.stop_client()

                start_time = time.time()
                check_time = start_time
                atlas.start_client()
                TRANSPORTS = atlas.get_all_transport()
                search_routes()

    except Exception as e:
        print(e)
