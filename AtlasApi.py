# -*- coding: utf-8 -*-

import json
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime


class AtlasApiConnect(object):

    def __init__(self, url='', moloch_url=None, username=None, password=None):
        self.url = url
        self.moloch_url = moloch_url
        self.username = username
        self.password = password
        self.success_status_code = [200, 201]
        self.unauthorized_status_code = [401]
        self.status_code_for_retry = [502, 503, 504, 422]
        self.user_session_id = ''
        self.user_token = ''
        self.user_connection_id = ''
        self.s = requests.Session()
        self.retries = Retry(total=5, backoff_factor=1, status_forcelist=self.status_code_for_retry)
        self.s.mount('https://', HTTPAdapter(max_retries=self.retries))

    # def __del__(self):
        # self.__logout()

    def get_url(self):
        return self.url

    def get_user_token(self):
        return self.user_token

    def get_user_connection_id(self):
        return self.user_connection_id

    def request(self, method_url, method_type, params=None, body=None):
        response = ''
        if method_type == 'get':
            response = self.__get(self.url + method_url, params)
        elif method_type == 'post':
            response = self.__post(self.url + method_url, params, body)
        elif method_type == 'put':
            response = self.__put(self.url + method_url, params, body)
        elif method_type == 'delete':
            response = self.__delete(self.url + method_url, params, body)
        return response

    def __get(self, url, params=None):
        result = None

        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}

        try:
            response = self.s.get(url, params=params, headers=headers)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __post(self, url, params=None, body=None):
        result = None

        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}

        try:
            response = self.s.post(url, params=params, headers=headers, json=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __put(self, url, params=None, body=None):
        result = None

        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}

        try:
            response = self.s.put(url, params=params, headers=headers, data=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
            else:
                print(url, response.status_code, response.content.decode())
        except Exception as e:
            print(e)
        return result

    def __delete(self, url, params=None, body=None):
        result = None

        headers = {'Authorization': 'Bearer ' + self.user_token,
                   'Content-Type': 'application/json; charset=utf-8'}
        try:
            response = self.s.delete(url, params=params, headers=headers, data=body)
            if response.status_code in self.success_status_code:
                result = response.json()
            elif response.status_code in self.unauthorized_status_code:
                print(url, response.status_code, response.content.decode())
                self.stop_client()
                self.start_client()
                time.sleep(2)
                result = self.__get(url, params)

                # result = response.json()
                # if 'Message' in result:
                #     if result['Message'] == 'Unauthorized':
                #         self.stop_client()
                #         self.start_client()
                #         time.sleep(2)
                #         self.__get(url, params, headers)
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
        response = self.request(method_url=method_url, method_type='post')
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
        self.__logout()
        self.s.close()

    '''Create order'''
    def create_order(self, op_type='Delivery', hub_code='01-01-КЛМ', route_external_id=None, carrier_code=None,
                     leg_external_id=None, delivery_from='2020-01-01T10:00:00.000Z',
                     delivery_to='2020-01-01T12:00:00.000Z', load_from='', load_to=''):
        order_number = 'OTBG-' + str(datetime.now())
        method_url = 'oms/api/Orders'
        body = {
                    "OrderInfo": {
                        "ExternalId": order_number,
                        "Number": order_number,
                        "OperationType": op_type
                    },
                    "AllocationInfo": {
                        "HubCode": hub_code,
                        "RouteExternalId": route_external_id,
                        "CarrierCode": carrier_code,
                        "TacticalLegExternalId": leg_external_id
                    },
                    "DeliveryTimeSlot": {
                        "From": delivery_from,
                        "To": delivery_to
                    },
                    # "LoadTimeSlot": {
                    #     "From": load_from,
                    #     "To": load_to
                    # },
                    "ContactInfo": {
                        "Name": "Иванов Иван Иванович",
                        "Phones": [
                            "+79999999999"
                        ]
                    },
                    "AddressInfo": {
                        "FullAddress": "Rue du Saint-Gothard, 11, Strasbourg, Франция. 67000",
                        "Country": "Россия",
                        "PostalCode": "193315",
                        "District": "Санкт-Петербург",
                        "Town": "Санкт-Петербург",
                        "Street": "проспект Большевиков",
                        "Building": "42"
                    },
                    "TransportRestrictionsInfo": {
                        "LoadUnloadTypes": [
                            "BothSide"
                        ],
                        "TransportRestrictions": ["MKAD"]
                    }
                }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nOrder creating failed')
        return response

    '''Create delivery order'''
    def create_delivery_order(self, order_number, op_type='Delivery', hub_code=None, route_external_id=None,
                              carrier_code=None, leg_external_id=None, transport_number=None,
                              delivery_from='2020-01-01T10:00:00.000Z', delivery_to='2020-01-01T12:00:00.000Z',
                              longitude='', latitude=''):
        method_url = 'oms/api/Orders'
        body = {
                    "OrderInfo": {
                        "ExternalId": order_number,
                        "Number": order_number,
                        "OperationType": op_type
                    },
                    "AllocationInfo": {
                        "HubCode": hub_code,
                        "RouteExternalId": route_external_id,
                        "CarrierCode": carrier_code,
                        "TacticalLegExternalId": leg_external_id,
                        "TransportNumber": transport_number
                    },
                    "DeliveryTimeSlot": {
                        "From": delivery_from,
                        "To": delivery_to
                    },
                    "ContactInfo": {
                        "Name": "Иванов Иван Иванович",
                        "Phones": [
                            "+79999999999"
                        ]
                    },
                    "LocationInfo": {
                        "Longitude": longitude,
                        "Latitude": latitude
                    }
                }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nOrder creating failed')
        return response

    '''Create pickup order'''
    def create_pickup_order(self, order_number, op_type='PickUp', hub_code=None, route_external_id=None,
                            carrier_code=None, leg_external_id=None, transport_number=None,
                            pickup_from='2020-01-01T10:00:00.000Z', pickup_to='2020-01-01T12:00:00.000Z',
                            longitude='', latitude=''):
        method_url = 'oms/api/Orders'
        body = {
            "OrderInfo": {
                "ExternalId": order_number,
                "Number": order_number,
                "OperationType": op_type
            },
            "AllocationInfo": {
                "HubCode": hub_code,
                "RouteExternalId": route_external_id,
                "CarrierCode": carrier_code,
                "TacticalLegExternalId": leg_external_id,
                "TransportNumber": transport_number
            },
            "PickupTimeSlot": {
                "From": pickup_from,
                "To": pickup_to
            },
            "ContactInfo": {
                "Name": "Иванов Иван Иванович",
                "Phones": [
                    "+79999999999"
                ]
            },
            "LocationInfo": {
                "Longitude": longitude,
                "Latitude": latitude
            }
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nOrder creating failed')
        return response

    '''Get route by order id'''
    def get_route_by_order_id(self, order_id):
        method_url = 'tms/api/Orders/' + order_id + '/Routes'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute receiving failed')
        return response

    '''Get lot by lot id'''
    def get_lot(self, lot_id):
        method_url = 'routeauctionquilt/api/lots/' + lot_id + '?Bets.WithBidderInfo=true'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nLot receiving failed')
        return response

    '''Create leg '''
    def create_leg(self, leg_external_id, stat_point_name, end_point_name):
        method_url = 'resources/api/tacticalLegs'
        body = {
            "ExternalId": leg_external_id,
            "StartPoint": {
                "Zone": {
                    "TimeOffsetInMinutes": 180,
                    "Name": stat_point_name
                }
            },
            "EndPoint": {
                "Zone": {
                    "TimeOffsetInMinutes": 180,
                    "Name": end_point_name
                }
            }
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nLeg creating failed')
        return response

    '''Create contracts for leg'''
    def create_contract_for_leg(self, leg_id, weight_type, carrier_id, ts_count):
        method_url = 'resources/api/tacticalLegs/' + leg_id + '/contracts/carriers'
        body = {
                    "Contracts": [
                        {
                            "WeightType": weight_type,
                            "CarrierInfos": [
                                {
                                    "CarrierId": carrier_id,
                                    "Price": 8100,
                                    "TransportCount": ts_count
                                }
                            ]
                        }
                    ]
                }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nLeg contracts failed')
        return response

    '''Auto carrier assigning'''
    def auto_assign(self, route_id):
        method_url = 'assigninggear/api/setRouteCarrier/auto'
        body = {
            "Routes": [
                {
                    "Id": route_id
                }
            ]
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nAuto assigning failed')
        return response

    '''Assigning carrier on route'''
    def assign_carrier_on_route(self, route_id, carrier_id):
        method_url = 'assigninggear/api/setRouteCarrier'
        body = {
            "RouteId": route_id,
            "CarrierId": carrier_id
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nCarrier assigning failed')
        return response

    '''Removing carrier on route'''
    def remove_carrier_from_route(self, route_id):
        method_url = 'assigninggear/api/setRouteCarrier'
        body = {
            "RouteId": route_id,
            "CarrierId": None
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nCarrier removing failed')
        return response

    '''Assigning performer on route'''
    def assign_performer_on_route(self, route_id, transport_id, performer_id):
        method_url = 'assigninggear/api/routePerformer/assign'
        body = {
                  "RouteId": route_id,
                  "TransportId": transport_id,
                  "PersonIds": [
                    performer_id
                  ]
                }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nPerformer assigning failed')
        return response

    '''Get all orders'''
    def get_orders(self):
        method_url = 'oms/api/Orders/All'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nOrders getting failed')
        return response

    '''Get all lots'''
    def get_lots(self):
        method_url = 'bidding/api/odata/biddinglot'
        params = {'$count': 'true',
                  '$filter': "(StateInfo/State eq 'Created' or StateInfo/State eq 'Started') and "
                             "LotInfo/Type eq 'Routes'",
                  '$select': 'Id',
                  '$skip': '0'}
        response = self.request(method_url=method_url, method_type='get', params=params)
        if response is None:
            print('\nLots getting failed')
        return response

    '''Get all lots with blitz rate'''
    def get_lots_with_blitz_rate(self):
        method_url = 'bidding/api/odata/biddinglot'
        params = {'$count': 'true',
                  '$filter': "(StateInfo/State eq 'Created' or StateInfo/State eq 'Started') and "
                             "LotInfo/Type eq 'Routes' and not(LotInfo/BlitzBetPrice eq null)",
                  '$select': 'Id',
                  '$skip': '0'}
        response = self.request(method_url=method_url, method_type='get', params=params)
        if response is None:
            print('\nLots getting failed')
        return response

    '''Get all users from moloch'''
    def get_users_from_moloch(self):
        method_url = 'api/users'
        response = self.__get(url=self.moloch_url+method_url)
        if response is None:
            print('\nUsers getting failed')
        return response

    '''Get company'''
    def get_company(self, company_id):
        method_url = 'resources/api/companies/' + company_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nCompany receiving failed')
        return response

    '''Add role for user'''
    def add_role_for_user(self, user_id, role):
        method_url = 'resources/api/users/' + user_id + '/roles'
        body = {
                    "Roles": [role]
                }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response

    '''Get leg'''
    def get_leg(self, leg_id):
        method_url = 'resources/api/tacticalLegs/' + leg_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nLeg receiving failed')
        return response

    '''Delete leg'''
    def remove_leg(self, leg_id):
        method_url = 'resources/api/tacticalLegs/' + leg_id
        response = self.request(method_url=method_url, method_type='delete')
        if response is None:
            print('\nLeg deleting failed')
        return response

    '''Get leg'''
    def get_all_legs(self):
        method_url = 'resources/api/tacticalLegs'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nLegs receiving failed')
        return response

    '''Get carrier queues'''
    def get_carrier_queues(self, leg_id, weight_type=None, skip_count=0):
        if weight_type is None:
            method_url = 'tacticalLegs/api/legs/' + leg_id + '/queues'
        else:
            method_url = 'tacticalLegs/api/legs/' + leg_id + '/queues?weightType=' + weight_type + '&skip=' + \
                         str(skip_count)
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nQueues receiving failed')
        return response

    '''Get carrier'''
    def get_carrier(self, carrier_id):
        method_url = 'resources/api/carriers/' + carrier_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nCarrier receiving failed')
        return response

    '''Get carrier'''
    def get_route(self, route_id):
        method_url = 'tms/api/Routes/' + route_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute receiving failed')
        return response

    '''Get gates by hub id'''
    def get_gates(self, hub_id):
        method_url = 'resources/api/hubs/' + hub_id + '/gates'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGates receiving failed')
        return response

    '''Get booking from gate'''
    def get_bookings(self, gate_id, date_from, date_to):
        method_url = 'bookingquilt/api/gates/' + gate_id + '/bookings?From=' + date_from + '&To=' + date_to
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nBookings receiving failed')
        return response

    '''Get user'''
    def get_user(self, user_id):
        method_url = 'resources/api/users/' + user_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nUser receiving failed')
        return response

    '''Get users info'''
    def get_users_info(self):
        method_url = 'auth/api/v1/User'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nUsers info receiving failed')
        return response

    '''Get users from company'''
    def get_users_from_company(self, company_id):
        method_url = 'resources/api/companies/' + company_id + '/users'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nUsers info receiving failed')
        return response

    '''Get all active route'''
    def get_active_routes(self):
        method_url = 'tms/api/Routes/All'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoutes receiving failed')
        return response

    '''Get route points by route id'''
    def get_route_points(self, route_id):
        method_url = 'tms/api/Routes/' + route_id + '/RoutePoints'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute points receiving failed')
        return response

    '''Get route point history'''
    def get_route_point_history(self, route_point_id):
        method_url = 'tms/api/RoutePoints/' + route_point_id + '/FullHistory'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute point history receiving failed')
        return response

    '''Get route by route point id'''
    def get_route_by_route_point_id(self, route_point_id):
        method_url = 'tms/api/RoutePoints/' + route_point_id + '/Routes'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute receiving failed')
        return response

    '''Get person by id'''
    def get_person(self, person_id):
        method_url = 'resources/api/persons/' + person_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nPerson receiving failed')
        return response

    '''Get transport by id'''
    def get_transport(self, transport_id):
        method_url = 'resources/api/transports/' + transport_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nTransport receiving failed')
        return response

    '''Get order by external id'''
    def get_order_by_external_id(self, order_external_id):
        method_url = 'oms/api/Orders/external/' + order_external_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nOrder receiving failed')
        return response

    '''Get order by id'''
    def get_order_by_id(self, order_id):
        method_url = 'oms/api/Orders/' + order_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nOrder receiving failed')
        return response

    '''Create route'''
    def create_route(self, route_name, route_start, route_end):
        method_url = 'tms/api/Routes'
        body = {
                    "RouteInfo": {
                        "Name": route_name,
                        "Start": route_start,
                        "End": route_end,
                        "ExternalId": route_name
                        }
                }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nRoute creating failed')
        return response

    '''Create route from json'''
    def create_route_from_json(self, body_json):
        method_url = 'tms/api/Routes'
        body = body_json
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nRoute creating failed')
        return response

    '''Create route point'''
    def create_route_point(self, route_id, point_latitude, point_longitude, planning_time, point_order,
                            point_type='Delivery'):
        method_url = 'tms/api/Routes/' + route_id + '/RoutePoints'
        body = {
                  "LocationInfo": {
                    "Longitude": point_longitude,
                    "Latitude": point_latitude
                  },
                  "PlanningInfo": {
                    "PlanningTime": planning_time
                  },
                  "RoutePointInfo": {
                    "PointType": point_type
                  },
                  "OrderingInfo": {
                    "Order": point_order
                  }
                }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nRoute point creating failed')
        return response

    '''Get route by external id'''
    def get_route_by_external_id(self, route_external_id):
        method_url = 'tms/api/Routes/External/' + route_external_id
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute receiving failed')
        return response

    '''Create order_task'''
    def create_order_task(self, route_point_id, order_id):
        method_url = 'tms/api/RoutePoints/' + route_point_id + '/OrderTasks'
        body = {
                  "OrderId": order_id
                }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nOrder task creating failed')
        return response

    '''Archive route'''
    def archive_route(self, route_id):
        method_url = 'tms/api/Routes/MoveToArchiveRoute/' + route_id
        response = self.request(method_url=method_url, method_type='delete')
        if response is None:
            print('\nRoute archiving failed')
        return response

    '''Move route'''
    def move_route(self, route_id):
        method_url = 'tms/api/Routes/' + route_id
        body = {
                    "RouteInfo": {
                        "Name": "Trash",
                        "Start": "2019-12-31T10:00:00.000Z",
                        "End": "2019-12-31T10:00:00.000Z",
                        "ExternalId": "Trash"
                        }
                }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nRoute creating failed')
        return response

    '''Get route by external id'''
    def get_all_route(self):
        method_url = 'tms/api/Routes/All'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoutes receiving failed')
        return response

    '''Get route history'''
    def get_route_history(self, route_id):
        method_url = 'tms/api/Routes/' + route_id + '/FullHistory'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute history receiving failed')
        return response

    '''Get route state history'''
    def get_route_state_history(self, route_id):
        method_url = 'tms/api/Routes/' + route_id + '/StateInfo/History'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nRoute state history receiving failed')
        return response

    '''Get order state history'''
    def get_order_state_history(self, order_id):
        method_url = 'oms/api/Orders/' + order_id + '/StateInfo/History'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nOrder state history receiving failed')
        return response

    '''Complete delivery order task'''
    def complete_delivery_order_task(self, order_task_id):
        method_url = 'orderquilt/api/OrderTasks/' + order_task_id + '/Delivery/Complete'
        body = {
                "comment": "script"
               }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nOrder tasks completing failed')
        return response

    '''Get carrier karma'''
    def get_carrier_karma(self, carrier_id):
        method_url = 'karmaapi/Carrier/' + carrier_id + '/Karma'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nCarrier karma receiving failed')
        return response

    '''Set state for route'''
    def set_route_state(self, route_id, route_state):
        method_url = 'tms/api/Routes/' + route_id + '/StateInfo'
        body = {
                "State": route_state
               }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response

    '''Create lot'''
    def create_lot(self, route_id, lot_start, lot_end, threshold_price=None):
        method_url = 'routeauctionquilt/api/lots'
        body = {
            "LotInfo": {
                "ThresholdPrice": threshold_price,
                "StartTime": lot_start,
                "EndTime": lot_end
            },
            "RouteIds": [route_id]
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nLot creating failed')
        return response

    '''Create bot for lot'''
    def create_bet(self, lot_id, bet_value):
        method_url = 'routeauctionquilt/api/lots/' + lot_id + '/bets'
        body = {
            "Price": bet_value
        }
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nBet creating failed')
        return response

    '''Get weight types dictionary'''
    def get_weight_types_dictionary(self):
        method_url = 'resources/api/dictionary/weightTypes'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nWeight types dictionary receiving failed')
        return response

    '''Get all transports'''
    def get_all_transport(self):
        method_url = 'resources/api/transports'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Update performer info for route'''
    def update_route_performer_info(self, route_id, transport_id, person_id):
        method_url = 'tms/api/Routes/' + route_id + '/PerformerInfo'
        body = {
            "TransportId": transport_id,
            "PersonIds": [person_id]
        }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response

    '''Get load unload types'''
    def get_load_unload_types(self):
        method_url = 'resources/api/dictionary/loadUnloadTypes'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get load unload restrictions'''
    def get_load_unload_restrictions(self):
        method_url = 'resources/api/dictionary/loadUnloadRestrictions'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get transport types'''
    def get_transport_types(self):
        method_url = 'resources/api/dictionary/transportTypes'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get zone restrictions'''
    def get_zone_restrictions(self):
        method_url = 'resources/api/dictionary/zoneRestrictions'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get board heights'''
    def get_board_heights(self):
        method_url = 'resources/api/dictionary/boardHeights'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get all carriers'''
    def get_all_carriers(self):
        method_url = 'resources/api/carriers/All'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get all persons'''
    def get_all_persons(self):
        method_url = 'resources/api/persons/All'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get schedule for person'''
    def get_schedule_by_person_id(self, person_id: str):
        method_url = 'resources/api/persons/' + person_id + '/schedules'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Get all users'''
    def get_all_users(self):
        method_url = 'resources/api/users'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nGET ' + method_url + ' Failed')
        return response

    '''Archive lot'''
    def archive_bidding_lot(self, bidding_lot_id: str):
        method_url = 'bidding/api/lots/archive'
        body = {
                "LotIds": [bidding_lot_id]
               }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response

    '''Cancel lot'''
    def cancel_bidding_lot(self, bidding_lot_id: str):
        method_url = 'routeauctionquilt/api/lots/' + bidding_lot_id + '/cancel'
        response = self.request(method_url=method_url, method_type='put')
        if response is None:
            print('\nPUT ' + method_url + ' Failed')
        return response

    '''Get lots by lot_ids'''
    # def get_lots_by_lots_ids(self, lots_ids: dict):
    #     method_url = 'routeauctionquilt/api/lots'
    #
    #     for i, lot in enumerate(lots_ids['value']):
    #         if i == 0:
    #             method_url += '?LotIds=' + lot['Id']
    #         else:
    #             method_url += '&LotIds=' + lot['Id']
    #
    #     response = self.request(method_url=method_url, method_type='get')
    #     if response is None:
    #         print('\nLots getting failed')
    #     return response

    '''Get lots by lot_ids'''
    def get_lots_by_lots_ids(self, lots_ids: list):
        method_url = 'routeauctionquilt/api/lots'

        for i, lot in enumerate(lots_ids):
            if i == 0:
                method_url += '?LotIds=' + lot['Id']
            else:
                method_url += '&LotIds=' + lot['Id']

        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nLots getting failed')
        return response

    '''Update order state'''
    def update_order_state(self, order_id: str, state: str):
        method_url = 'oms/api/Orders/' + order_id + '/StateInfo'
        body = {
                  "State": state
                }
        response = self.request(method_url=method_url, method_type='put', body=json.dumps(body))
        if response is None:
            print('\nOrder state updating failed')
        return response

    '''Create ETA for order'''
    def create_eta_for_order(self, order_id: str, eta: str):
        method_url = 'mobile/api/Eta/Update'
        body = [
                  {
                    "OrderId": order_id,
                    "EstimatedArrivalTime": eta,
                    "CalculatedOn": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                  }
                ]
        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nOrder ETA creating failed')
        return response

    '''Create ETA for order (moloch)'''
    def create_eta_for_order_from_moloch(self, order_id: str, eta: str):
        method_url = 'v1/taskPredictions'
        body = [
                  {
                    "CalculatedOn": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "CreatedOn": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "EstimatedArrivalTime": eta,
                    "TaskId": order_id
                  }
                ]

        response = self.__post(url=self.moloch_url+method_url, body=body)
        if response is None:
            print('\nOrder ETA creating failed')
        return response

    '''Create event "ReachedTheClient" for order'''
    def create_event_reach_the_client(self, order_id: str):
        method_url = 'oms/api/Orders/' + order_id + '/Events'
        body = {
                  "EventType": "ReachedTheClient",
                  "EventData": []
                }

        response = self.request(method_url=method_url, method_type='post', body=body)
        if response is None:
            print('\nOrder event creating failed')
        return response

    '''Get analytics'''
    def get_analytics(self, date_from: str, date_to: str, hub_ids=None, carrier_ids=None):
        method_url = 'analytics/api/v1/report?dateFrom=' + date_from + '&dateTo=' + date_to

        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nAnalytics getting failed')
        return response

    '''Get all hubs'''
    def get_all_hubs(self):
        method_url = 'resources/api/hubs/all'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nHubs getting failed')
        return response

    '''Get preset'''
    def get_preset(self):
        method_url = 'settings/api/v1/Preset'
        response = self.request(method_url=method_url, method_type='get')
        if response is None:
            print('\nPreset getting failed')
        return response

    '''Get all lots'''
    def get_routes(self):
        method_url = 'tms/api/odata/route'
        params = {'$count': 'false',
                  '$expand': 'BreakInfo($select=Start,End),'
                             'CarrierInfo($select=CarrierId),'
                             'CompanyInfo($select=CompanyId),'
                             'HubInfo($select=HubId),'
                             'PerformerInfo($select=TransportId,PersonIds),'
                             'RouteInfo($select=Name,Start,End),'
                             'RoutePoints,'
                             'StateInfo($select=State),'
                             'TransportRestrictionsInfo($select=LoadUnloadTypes,TransportRestrictions)',
                  '$select': 'Id',
                  '$skip': '0'}
        response = self.request(method_url=method_url, method_type='get', params=params)
        if response is None:
            print('\nRoutes getting failed')
        return response


'''

def get_token(self):
    status, message = get_session_id(company_url, username, password)
    if status in success_status_code:
        session_id = message
        params = {'sessionId': session_id}
        url = company_url + 'auth/api/v1/Token/sessionId'
        r = requests.post(url, params=params)
        if r.status_code in success_status_code:
            data = r.json()
            if 'token' in data:
                print(str(r.status_code) + ' Token: ' + data['token'])
                return r.status_code, data['token']
            else:
                return r.status_code, "Token data error"
        else:
            return r.status_code, "Token error"
    else:
        return status, message




def get_session_id(company_url, username, password):
    url = company_url + 'auth/api/v1/Login'
    r = requests.post(url, json={"username": username, "password": password})
    if r.status_code in success_status_code:
        data = r.json()
        if 'sessionId' in data:
            print(str(r.status_code) + ' SessionId: ' + data['sessionId'])
            return r.status_code, data['sessionId']
        else:
            return r.status_code, 'SessionId data error'
    else:
        return r.status_code, 'SessionId error'


def get_token(company_url, username, password):
    status, message = get_session_id(company_url, username, password)
    if status in success_status_code:
        session_id = message
        params = {'sessionId': session_id}
        url = company_url + 'auth/api/v1/Token/sessionId'
        r = requests.post(url, params=params)
        if r.status_code in success_status_code:
            data = r.json()
            if 'token' in data:
                print(str(r.status_code) + ' Token: ' + data['token'])
                return r.status_code, data['token']
            else:
                return r.status_code, "Token data error"
        else:
            return r.status_code, "Token error"
    else:
        return status, message


def get_connection_id(company_url, token):
    params = {'AUTH_TOKEN': token}
    url = company_url + 'notify/api/signalr/negotiate'
    r = requests.post(url, params=params)
    if r.status_code in success_status_code:
        data = r.json()
        if 'connectionId' in data:
            print(str(r.status_code) + ' ConnectionId: ' + data['connectionId'])
            return r.status_code, data['connectionId']
        else:
            return r.status_code, 'ConnectionId data error'
    else:
        return r.status_code, 'ConnectionId error'


def get_lots(token, company_url):
    headers = {'Authorization': 'Bearer ' + token}
    params = {'$count': 'true',
              '$filter': "(StateInfo/State eq 'Created' or StateInfo/State eq 'Started') and LotInfo/Type eq 'Routes'",
              '$select': 'Id',
              '$skip': '0',
              '$top': '20'}
    url = company_url + 'bidding/api/odata/biddinglot'
    r = requests.get(url, headers=headers, params=params)
    if r.status_code in success_status_code:
        data = r.json()
        if 'value' in data:
            return r.status_code, data
        else:
            return r.status_code, 'Lots getting data error'
    else:
        return r.status_code, 'Lots getting error'


def get_lot_info(token, lot_id, company_url):
    headers = {'Authorization': 'Bearer ' + token}
    url = company_url + 'routeauctionquilt/api/lots/' + lot_id + '?Bets.WithBidderInfo=true'
    r = requests.get(url, headers=headers)
    data = r.json()
    if r.status_code in success_status_code:
        return r.status_code, data
    else:
        return r.status_code, "Lot info getting error"
'''