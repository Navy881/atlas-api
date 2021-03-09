# -*- coding: utf-8 -*-
import random

import requests
import time
import json

success_status_code = [200, 201]

company_url = ''
username = ''
password = ''

route_states = ['Created', 'Planning', 'NotPlanned', 'Planned', 'CarrierAssigning', 'CarrierNotAssigned',
                'CarrierAssigned', 'CarrierAccepted', 'CarrierRejected', 'PerformerAssigning', 'PerformerNotAssigned',
                'PerformerAssigned', 'SentToPerformer', 'PerformerAccepted', 'PerformerRejected', 'Prestart',
                'ArrivedForLoading', 'ReadyForLoading', 'LoadingStarted', 'LoadingFinished', 'Started',
                'ArrivingForUnloading', 'ReadyForUnloading', 'UnloadingStarted', 'UnloadingFinished', 'Finished',
                'Returning', 'Completed']


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


def create_route(token, name, state):
    headers = {'Authorization': 'Bearer '+token,
               'Content-Type': 'application/json; charset=utf-8'}
    data = {
            "RouteInfo": {
                "Name": name,
                "Start": "2015-01-01T10:00:00.000Z",
                "End": "2015-01-01T12:00:00.000Z",
                "ExternalId": name
            },
            "CarrierInfo": {
                "CarrierId": "2ff9bf78-043f-49fd-9c96-a9a600bcd4c8",
            },
            "StateInfo": {
                "State": state
            }
        }
    url = company_url + 'tms/api/Routes'
    r = requests.post(url, headers=headers, data=json.dumps(data))
    if r.status_code in success_status_code:
        return r.status_code
    else:
        return r.status_code


def main():
    status, message = get_token()
    if status == "Ok":
        token = message
        for i in range(0, len(route_states)):
            name = 'TESTROUTE_' + str(random.randint(1, 10000)) + '_' + str(i)
            state = route_states[i]
            print(name, state)
            status = create_route(token, name, state)
            print(status)
            time.sleep(1)
    else:
        return status, message


if __name__ == '__main__':
    try:
        print("bot running...")
        main()
    except Exception as e:
        print(e)
