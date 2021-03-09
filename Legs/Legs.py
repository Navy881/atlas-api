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


def get_legs(token):
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json; charset=utf-8'}
    url = company_url + 'resources/api/tacticalLegs'
    r = requests.get(url, headers=headers)
    if r.status_code in success_status_code:
        data = r.json()
        message = data
    else:
        message = 'Error'
    return r.status_code, message


def main():
    status, message = get_token()
    if status == "Ok":
        token = message
        status, message = get_legs(token)
        if status in success_status_code:
            print('\n')
            legs_data = message
            for leg in legs_data:
                if 'ExternalId' in leg:
                    print('Leg ' + str(legs_data.index(leg) + 1) + ': ' + leg['StartPoint']['Zone']['Name'] + ' - ' +
                          leg['EndPoint']['Zone']['Name'] + ', ExternalId: ' + leg['ExternalId'] + ', Id: ' + leg['Id'])
                else:
                    print('Leg ' + str(legs_data.index(leg) + 1) + ': ' + leg['StartPoint']['Zone']['Name'] + ' - ' +
                          leg['EndPoint']['Zone']['Name'] + ', Id: ' + leg['Id'])
    input('Press any key...')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
