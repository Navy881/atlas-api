# -*- coding: utf-8 -*-

import requests
import time
import logging
import json
import telepot
from telepot.loop import MessageLoop

company_url = ''
username = ''
password = ''

# Open json-file for read
def readConfig():
    with open('config.json', 'r') as f:
        data = json.loads(f.read())
    return data


# Read bot parameters
def getBotParameters():
    data = readConfig()
    
    BOT_TOKEN = data['BotParameters']['token'] # bot token
    PROXY_URL = data['BotParameters']['proxy_url'] # proxy-server address
    MY_CHAT_ID = data['BotParameters']['chat_id'] # chat id with bot
    SENDING_PERIOD = data['BotParameters']['sending_period'] # message sending period in to chat by bot
    USERNAME = data['BotParameters']['username'] # proxy username
    PASSWORD = data['BotParameters']['password'] # proxy password

    # Proxy parameters
    REQUEST_KWARGS={'proxy_url': PROXY_URL}
    
    return BOT_TOKEN, REQUEST_KWARGS, MY_CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD


BOT_TOKEN, REQUEST_KWARGS, CHAT_ID, PROXY_URL, _, USERNAME, PASSWORD = getBotParameters()
# Proxy
SetProxy = telepot.api.set_proxy(PROXY_URL, (USERNAME, PASSWORD))
bot = telepot.Bot(BOT_TOKEN)


def get_sessionId(username, password):
    url = company_url+'auth/api/v1/Login'
    r = requests.post(url, json={"username": username, "password": password})
    print('\n'+r.url)
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
        url = company_url+'auth/api/v1/Token/sessionId'
        r = requests.post(url, params=params)
        print('\n'+r.url)
        data = r.json()
        if 'token' in data:
            print('Token Ok: ' + data['token'])                             
            return 'Ok', data['token']
        else:                           
            return 'Token error.', data['message']
    else:
        return status, message

def get_lots(token):
    headers = {'Authorization': 'Bearer '+token}
    params = {'$count': 'true',
              '$filter': "(StateInfo/State eq 'Created' or StateInfo/State eq 'Started') and LotInfo/Type eq 'Routes'",
              '$select': 'Id',
              '$skip': '0',
              '$top': '20'}
    url = company_url+'bidding/api/odata/biddinglot'
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    #print('\n'+r.url)
    if 'value' in data:
        #print('Lots: ' + str(data['@odata.count']))                             
        return 'Ok', data
    else:
        return 'Lots getting error', data


def get_lots_info(token, lotId):
    headers = {'Authorization': 'Bearer '+token}
    url = company_url+'routeauctionquilt/api/lots/'+lotId
    r = requests.get(url, headers=headers)
    data = r.json()
    return data
    
    

def notification():
    status, message = get_token()
    if status == 'Ok':
        token = message
        counter = 0
        last_lotId = ''
        while True:
            status, message = get_lots(token)
            if status == 'Ok':
                #print('Ok')
                data = message
                lots_count = data['@odata.count']
                if lots_count != 0 and data['value'][lots_count-1]['Id'] != last_lotId:
                    if lots_count == counter or lots_count > counter:
                        lotId = data['value'][lots_count-1]['Id']
                        lot_info = get_lots_info(token, lotId)
                        print('\nNew lot: '+str(lot_info['Routes'][0]['Name']))
                        bot_message = 'New lot: '+str(lot_info['Routes'][0]['Name'])
                        bot.sendMessage(CHAT_ID, bot_message)
                        counter = lots_count
                        last_lotId = data['value'][lots_count-1]['Id']
                    else:
                        counter = lots_count
                        last_lotId = data['value'][lots_count-1]['Id']
            else:
                return status, message
            time.sleep(5)
    else:
        return status, message

def main(msg):
    # Определение типа сообещения, типа чата и id чата
    content_type, chat_type, chat_id = telepot.glance(msg)
    #print(chat_id)


if __name__ == '__main__':
    try:
        print("bot running...")
        # Enable logging
        #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        #logger = logging.getLogger(__name__)
        MessageLoop(bot, main).run_as_thread()
        notification()
        while 1:
            time.sleep(10)
    except Exception as e:
        print(e)




