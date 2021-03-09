#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import logging
import json
import numpy as np
import slack
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

from AtlasApi import AtlasApiConnect

CONFIG_FILE = 'config.json'
USERS_DATA_FILE = 'users_data.json'
INPUT_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
OUTPUT_DATETIME_FORMAT = '%d.%m.%y %H:%M'
_USERS = {}
_MAX_IDS_TO_URL = 100

# _USER_DATA_FORMAT = {
#     "PhoneNumber": None,
#     "Login": False,
#     "CompanyId": '',
#     "CompanyName": '',
#     "GetAllLotsTries": 0,
#     "GetNearbyLotsTries": 0,
#     "LastLocation": {
#         "Latitude": None,
#         "Longitude": None
#     },
#     "GetFullLotInfoTries": [],
#     "SetBlitzRateTries": [],
#     "RadiusRequesting": False
# }


def get_data(json_file_path: str):
    try:
        with open(json_file_path, 'r') as f:
            data = json.loads(f.read())

        result = data
    except Exception as e:
        print('ERROR: file ' + json_file_path + ' reading:', e)
        result = None
    return result


def save_to_json(json_file_path: str, data: dict):
    try:
        with open(json_file_path, 'w') as fp:
            json.dump(data, fp)
    except Exception as e:
        print('ERROR: file ' + json_file_path + ' writing:', e)


SETTINGS = get_data(CONFIG_FILE)
if SETTINGS is None:
    sys.exit()

telegram_bot_settings = SETTINGS['TelegramBotParameters']
slack_settings = SETTINGS['SlackApiParameters']
atlas_settings = SETTINGS['AtlasAPIParameters']
private_chat_id = telegram_bot_settings['chat_id']
MAX_RADIUS = SETTINGS['MaxRadius']
TIME_OFFSET = SETTINGS['TimeOffset']
MAX_INLINE_BUTTONS = SETTINGS['MaxInlineButtons']

telegram_bot = telebot.TeleBot(telegram_bot_settings['token'])

atlas = AtlasApiConnect(url=atlas_settings['uri'],
                        moloch_url=atlas_settings['moloch_uri'],
                        username=atlas_settings['username'],
                        password=atlas_settings['password'])
atlas.start_client()

''' Slack client '''
slack_bot = slack.WebClient(token=slack_settings['token'])


def date_shift(datetime_str: str, hours: int = 3):
    datetime_str = datetime_str.split('Z')[0].split('.')[0]
    datetime_obj = datetime.strptime(datetime_str, INPUT_DATETIME_FORMAT)
    datetime_obj = datetime_obj + timedelta(hours=hours)
    datetime_str_o = datetime_obj.strftime(OUTPUT_DATETIME_FORMAT)
    return datetime_str_o


def send_message(chat_id: str, chat_type: str, message: str, parse_mode: str, reply_markup):
    current_time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    telegram_bot.send_message(chat_id=chat_id,  # id чата пользователя
                              text=message,  # сообщение
                              parse_mode=parse_mode,  # тип разметки сообщения
                              reply_markup=reply_markup,  # формат меню
                              disable_web_page_preview=True)  # отображение превью ссылки
    print("{} - bot answered into {} chat: {}".format(current_time, chat_type, chat_id))


def send_message_to_slack(slack_channel_id: str, route_name: str, blitz_rate: str, company_name: str):
    slack_bot.chat_postMessage(
        channel=slack_channel_id,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "@channel\n:robot_face: *Lot completed:* " + route_name + " with a telegram bot"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• Blitz rate price time: " + blitz_rate + "\n• Winner: " + company_name
                }
            },
            {
                "type": "divider"
            }
        ]
    )
    message = 'Lot completed:* ' + route_name + ' with a telegram bot' + '\n\n• Blitz rate price time:: ' + \
              blitz_rate + '\n• Winner: ' + company_name
    print('\n' + message + '\n')


def haversine_np(lon1: float, lat1: float, lon2: float, lat2: float):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    All args must be of equal length.
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km


# def main_markup():
#     markup = InlineKeyboardMarkup()
#     markup.row_width = 1
#     markup.add(InlineKeyboardButton('Показать все доступные рейсы', callback_data='cb_get_lots'))
#     markup.add(InlineKeyboardButton('Авторизоваться', callback_data='cb_auth'))
#     markup.add(InlineKeyboardButton('О боте', callback_data='cb_help'))
#     return markup


def main_markup2(chat_id: str):
    save_to_json(json_file_path=USERS_DATA_FILE, data=_USERS)

    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    button_all_lots = KeyboardButton(text='Показать все рейсы')
    button_geo = KeyboardButton(text='Показать ближайшие рейсы', request_location=True)
    button_help = KeyboardButton(text='Помощь')
    button_feedback = KeyboardButton(text='Обратная связь')
    button_contacts = KeyboardButton(text='Авторизоваться', request_contact=True)
    button_report = KeyboardButton(text='Отчёт')
    button_atlas_restart = KeyboardButton(text='Reauth in Atlas')
    markup.add(button_all_lots, button_geo, button_help, button_feedback)
    if not _USERS[chat_id]['Login']:
        markup.add(button_contacts)
    if str(chat_id) in private_chat_id:
        markup.add(button_report)
        markup.add(button_atlas_restart)
    return markup


def cancel_radius_message_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Отмена", callback_data="cb_radius_cancel"))
    return markup


def cancel_feedback_message_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Отмена", callback_data="cb_feedback_cancel"))
    return markup


def create_lots_markup(lots_info: dict):
    markup = InlineKeyboardMarkup()
    markup.row_width = len(lots_info)
    for lot in lots_info:
        markup.add(InlineKeyboardButton(lots_info[lot], callback_data="cb_lot_" + lot))
    return markup


def lot_markup(lot_id: str, blitz_rate: int = None):
    save_to_json(json_file_path=USERS_DATA_FILE, data=_USERS)

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if blitz_rate is not None:
        markup.add(InlineKeyboardButton('Забрать за ' + str(blitz_rate) + ' ₽ (без НДС)',
                                        callback_data="cb_blitz_" + lot_id))
    markup.add(InlineKeyboardButton('Показать ещё рейсы', callback_data="cb_get_lots"))
    return markup


def send_start_message(chat_type: str, chat_id: str):
    message_text = '*Привет\!*\n\n' \
                   'Я telegram\-бот компании [Atlas Chain](https://atlaschain.ru/?utm_source=TelegramBot)\.\n' \
                   'С помощью меня вы можете узнать о наличии доступных рейсов и зарезервировать их\.\n' \
                   'Более подборную инфрмацию о возможностях бота вы можете прочитать, нажав на кнопку «*_О боте_*»\.'
    send_message(chat_id=chat_id, chat_type=chat_type, message=message_text, parse_mode='MarkdownV2',
                 reply_markup=main_markup2(chat_id=chat_id))


def send_help_info(chat_type: str, chat_id: str):
    logging.info('User {} tried to request help info'.format(chat_id))
    message = '*Информация о боте:*\n\n' \
              'Я telegram\-бот компании [Atlas Chain](https://atlaschain.ru/?utm_source=TelegramBot)\.\n' \
              'С помощью меня вы можете узнать о наличии доступных рейсов и зарезервировать их\.\n\n' \
              '*Подробнее о возможностях:*\n' \
              ' • Для запроса всех доступных рейсов нажмите в меню кнопку «*_Показать все доступные рейсы_*»\n\n' \
              ' • Для запроса ближайших доступных рейсов нажмите в меню на кнопку «*_Показать ближайшие рейсы_*»\n\n' \
              ' • По каждому рейсы вы посмотреть подробную информацию нажав на него\n\n' \
              ' • Для выкупа рейса вам необходимо авторизоваться по кнопке «*_Авторизоваться_*»\n\n' \
              ' • Если ваш номер телефона есть в базе, то вы сможете выкупить рейс\. ' \
              'Выкупленный рейс будет автоматически назначен на вашу ТК'
    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='MarkdownV2',
                 reply_markup=main_markup2(chat_id=chat_id))


def send_sign_of_life(chat_type: str, chat_id: str):
    logging.info('User {} tried to request sign of life'.format(chat_id))
    send_message(chat_id=chat_id, chat_type=chat_type, message="I'm work", parse_mode='Markdown',
                 reply_markup=main_markup2(chat_id=chat_id))


def send_lots(chat_type: str, chat_id: str):
    logging.info('User {} tried to request all lots'.format(chat_id))
    _USERS[chat_id]['GetAllLotsTries'] += 1

    message = 'Пожалуйста, подождите. Поиск рейсов может занять некоторое время\n'
    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                 reply_markup=main_markup2(chat_id=chat_id))

    # Запрос данных о лотамх по списку ids из odata по 100 штук за одни запрос
    lots_from_odata = atlas.get_lots_with_blitz_rate()
    if '@odata.count' in lots_from_odata and 'value' in lots_from_odata and len(lots_from_odata['value']) > 0:
        if lots_from_odata['@odata.count'] > _MAX_IDS_TO_URL:
            lots = []
            for i in range((lots_from_odata['@odata.count'] // _MAX_IDS_TO_URL) + 1):
                lots += atlas.get_lots_by_lots_ids(lots_ids=lots_from_odata['value'][i*_MAX_IDS_TO_URL:
                                                                                     (i + 1)*_MAX_IDS_TO_URL])
        else:
            lots = atlas.get_lots_by_lots_ids(lots_ids=lots_from_odata['value'])
    else:
        lots = None

    if lots is not None and len(lots) > 0:
        lots_info = {}
        lots_markups = []

        lots_quantity = len(lots)
        print('All lots: ' + str(lots_quantity))
        message = '*Найдено рейсов: *' + str(lots_quantity)

        for i, lot in enumerate(lots):
            lot_start_location = lot['Path']['Start']['LocationName']
            if 'FullAddress' in lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']:
                lot_end_location = lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']['FullAddress']
            else:
                lot_end_location = ''
            route_start_time = date_shift(lot['Path']['Start']['ArrivalTime'], TIME_OFFSET)
            route_end_time = date_shift(lot['Path']['End']['ArrivalTime'], TIME_OFFSET)
            lots_info[lot['Id']] = lot_start_location + ' - ' + \
                                   lot_end_location + ', ' + \
                                   route_start_time + ' - ' + \
                                   route_end_time

            if (i != 0 and (i + 1) % MAX_INLINE_BUTTONS == 0) or i == lots_quantity - 1:
                lots_markups.append(lots_info)
                lots_info = {}

        for lots_markup in lots_markups:
            send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                         reply_markup=create_lots_markup(lots_info=lots_markup))
            message = '...'

    else:
        message = 'Пока рейсов нет'
        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))


def send_nearby_lots(chat_type: str, chat_id: str, latitude: float, longitude: float, radius: int):
    _USERS[chat_id]['GetNearbyLotsTries'] += 1

    message = 'Пожалуйста, подождите. Поиск рейсов может занять некоторое время\n'
    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                 reply_markup=main_markup2(chat_id=chat_id))

    # Запрос данных о лотамх по списку ids из odata по 100 штук за одни запрос
    lots_from_odata = atlas.get_lots_with_blitz_rate()
    if '@odata.count' in lots_from_odata and 'value' in lots_from_odata and len(lots_from_odata['value']) > 0:
        if lots_from_odata['@odata.count'] > _MAX_IDS_TO_URL:
            lots = []
            for i in range((lots_from_odata['@odata.count'] // _MAX_IDS_TO_URL) + 1):
                lots += atlas.get_lots_by_lots_ids(lots_ids=lots_from_odata['value'][i*_MAX_IDS_TO_URL:
                                                                                     (i + 1)*_MAX_IDS_TO_URL])
        else:
            lots = atlas.get_lots_by_lots_ids(lots_ids=lots_from_odata['value'])
    else:
        lots = None

    if lots is not None and len(lots) > 0:
        lots_info = {}
        lots_markups = []

        lots_quantity = len(lots)
        message = '*Рейсы в радиусе ' + str(radius) + ' км.:*'
        i = 0

        for j, lot in enumerate(lots):
            lot_start_latitude = lot['Path']['Start']['LocationInfo']['Latitude']
            lot_start_longitude = lot['Path']['Start']['LocationInfo']['Longitude']
            distance = haversine_np(lon1=longitude, lat1=latitude,
                                    lon2=lot_start_longitude, lat2=lot_start_latitude)
            if distance <= radius:
                i += 1
                lot_start_location = lot['Path']['Start']['LocationName']
                if 'FullAddress' in lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']:
                    lot_end_location = lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']['FullAddress']
                else:
                    lot_end_location = ''
                route_start_time = date_shift(lot['Path']['Start']['ArrivalTime'], TIME_OFFSET)
                route_end_time = date_shift(lot['Path']['End']['ArrivalTime'], TIME_OFFSET)
                lots_info[lot['Id']] = lot_start_location + ' - ' + \
                                       lot_end_location + ', ' + \
                                       route_start_time + ' - ' + \
                                       route_end_time

            if i != 0 and (i % MAX_INLINE_BUTTONS == 0 or j == lots_quantity - 1) and len(lots_info.keys()) > 0:
                lots_markups.append(lots_info)
                lots_info = {}

        if i > 0:
            print('Nearby lots: ' + str(i))
            for lots_markup in lots_markups:
                send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                             reply_markup=create_lots_markup(lots_info=lots_markup))
                message = '...'

        elif i == 0:
            message = 'Рейсов в радиусе ' + str(radius) + ' км. нет'
            send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                         reply_markup=main_markup2(chat_id=chat_id))

    else:
        message = 'Рейсов в радиусе ' + str(radius) + ' км. нет'
        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))


def send_full_lot_info(chat_type: str, chat_id: str, lot_id: str):
    _USERS[chat_id]['GetFullLotInfoTries'].append(lot_id)

    lot = atlas.get_lot(lot_id=lot_id)

    if lot is not None:
        weight_types = atlas.get_weight_types_dictionary()
        load_unload_types = atlas.get_load_unload_types()
        load_unload_restrictions = atlas.get_load_unload_restrictions()
        transport_types = atlas.get_transport_types()
        zone_restrictions = atlas.get_zone_restrictions()
        board_heights = atlas.get_board_heights()

        if weight_types is None:
            weight_types = []

        if load_unload_types is None:
            load_unload_types = []

        if load_unload_restrictions is None:
            load_unload_restrictions = []

        if transport_types is None:
            transport_types = []

        if zone_restrictions is None:
            zone_restrictions = []

        if board_heights is None:
            board_heights = []

        lot_name = lot['Routes'][0]['Name']
        lot_start_location = lot['Path']['Start']['LocationName']
        if 'FullAddress' in lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']:
            lot_end_location = lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']['FullAddress']
        else:
            lot_end_location = ''
        route_start_time = date_shift(lot['Path']['Start']['ArrivalTime'], TIME_OFFSET)
        route_end_time = date_shift(lot['Path']['End']['ArrivalTime'], TIME_OFFSET)
        lot_restrictions = ''
        for load_unload_type in load_unload_types:
            if 'LoadUnloadType' in lot['TransportRestrictionsInfo'] and \
                    lot['TransportRestrictionsInfo']['LoadUnloadType'] == load_unload_type['LoadUnloadType']:
                lot_restrictions += ' • ' + load_unload_type['Title'] + '\n'
        for restriction in lot['TransportRestrictionsInfo']['TransportRestrictions']:
            for weight_type in weight_types:
                if restriction == str(weight_type['WeightType']):
                    lot_restrictions += ' • ' + weight_type['Title'] + '\n'
            for load_unload_restriction in load_unload_restrictions:
                if restriction == load_unload_restriction['LoadUnloadRestriction']:
                    lot_restrictions += ' • ' + load_unload_restriction['Title'] + '\n'
            for transport_type in transport_types:
                if restriction == transport_type['TransportType']:
                    lot_restrictions += ' • ' + transport_type['Title'] + '\n'
            for zone_restriction in zone_restrictions:
                if restriction == zone_restriction['ZoneRestriction']:
                    lot_restrictions += ' • ' + zone_restriction['Title'] + '\n'
            for board_height in board_heights:
                if restriction == board_height['BoardHeight']:
                    lot_restrictions += ' • ' + board_height['Title'] + '\n'

        lot_end_time = date_shift(lot['LotInfo']['EndTime'], TIME_OFFSET)

        lot_blitz_rate = None
        if 'BlitzBetPrice' in lot['LotInfo']:
            lot_blitz_rate = lot['LotInfo']['BlitzBetPrice']

        message = '*Рейс:* ' + lot_name + '\n' + \
                  '*Откуда:* ' + lot_start_location + '\n' + \
                  '*Куда:* ' + lot_end_location + '\n' + \
                  '*Когда:* ' + route_start_time + ' - ' + route_end_time + '\n' + \
                  '*Условия:*\n' + lot_restrictions + '\n' + \
                  '*Активен до:* ' + lot_end_time

        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=lot_markup(lot_id=lot_id, blitz_rate=lot_blitz_rate))

    else:
        send_message(chat_id=chat_id, chat_type=chat_type, message='Лот больше недоступен', parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))


def get_user_token(username: str, password: str):
    user_atlas_client = AtlasApiConnect(url=atlas_settings['uri'], username=username, password=password)
    user_atlas_client.start_client()
    token = user_atlas_client.get_user_token()
    user_atlas_client.stop_client()
    if token == '':
        token = None
    return token


def set_blitz_rate(chat_type: str, chat_id: str, lot_id: str):
    _USERS[chat_id]['SetBlitzRateTries'].append(lot_id)

    if _USERS[chat_id]['Login'] and _USERS[chat_id]['PhoneNumber'] is not None:
        user_phone_number = _USERS[chat_id]['PhoneNumber']
        if check_user_by_number(chat_id=chat_id, phone_number=user_phone_number):
            lot = atlas.get_lot(lot_id=lot_id)
            if lot is not None and lot['StateInfo']['State'] == 'Started' and len(lot['Routes']) > 0:
                route_id = lot['Routes'][0]['Id']
                atlas.cancel_bidding_lot(bidding_lot_id=lot['Id'])

                # # TODO Сделать вместо этого завершение лота
                # atlas_2 = AtlasApiConnect(url=atlas_settings['uri'],
                #                           moloch_url=atlas_settings['moloch_uri'],
                #                           username='valve',
                #                           password='dev')
                # atlas_2.start_client()
                # atlas_2.create_bet(lot_id=lot['Id'], bet_value=lot['LotInfo']['BlitzBetPrice'])
                # atlas_2.stop_client()
                #
                # # TODO Маршрут не сразу получает статус доступный для назначения перевозчика.
                # # После появления метода отмены лота ответ будет приходить только после смены статуса маршрута
                # time.sleep(5)

                route = atlas.get_route(route_id=route_id)  # TODO
                if route['StateInfo']['State'] == 'CarrierNotAssigned':  # TODO
                    # atlas.remove_carrier_from_route(route_id=route_id)
                    response = atlas.assign_carrier_on_route(route_id=route_id, carrier_id=_USERS[chat_id]['CompanyId'])

                    if response is not None:
                        send_message_to_slack(slack_channel_id=slack_settings['channel_id'],
                                              route_name=lot['Routes'][0]['Name'],
                                              blitz_rate=str(lot['LotInfo']['BlitzBetPrice']),
                                              company_name=_USERS[chat_id]['CompanyName'])
                        message = 'Вы забрали рейс: ' + lot['Routes'][0]['Name'] + '.\n' \
                                                                                   'Стоимость рейса: ' + str(
                            lot['LotInfo']['BlitzBetPrice']) + ' руб.\n' \
                            'Рейс автоматически назначен на вашу компанию на платформе Atlas Chain.\n' \
                            'Для просмотра и назначения рейса на водителя перейдите на ' \
                            '[платформу](https://cloud.atlaschain.ru).'
                    else:
                        message = 'Что-то пошло не так.\nПопробуйте ещё раз.'
                else:
                    message = 'Что-то пошло не так.\nПопробуйте ещё раз.'
            else:
                message = 'Лот больше недоступен'
        else:
            _USERS[chat_id]['Login'] = False
            message = 'Вы не авторизованы.\nДля авторизации нажмите на кнопку «*Авторизоваться*» в главном меню.'
    else:
        message = 'Вы не авторизованы.\nДля авторизации нажмите на кнопку «*Авторизоваться*» в главном меню.'
    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                 reply_markup=main_markup2(chat_id=chat_id))


# Отправка расширенного отчёта в .csv
def send_advanced_report(chat_type: str, chat_id: str):
    logging.info('User {} tried to request advanced report'.format(chat_id))

    advanced_report_filename = 'advanced_report_' + str(datetime.now()).split(' ')[0] + ' ' + \
               str(datetime.now()).split(' ')[1].split(':')[0] + '-' + \
               str(datetime.now()).split(' ')[1].split(':')[1] + '-' + \
               str(datetime.now()).split(' ')[1].split(':')[2].split('.')[0] + \
               '.csv'
    f_ar = open(advanced_report_filename, "a", encoding="utf-16")

    feedback_report_filename = 'feedback_report_' + str(datetime.now()).split(' ')[0] + ' ' + \
               str(datetime.now()).split(' ')[1].split(':')[0] + '-' + \
               str(datetime.now()).split(' ')[1].split(':')[1] + '-' + \
               str(datetime.now()).split(' ')[1].split(':')[2].split('.')[0] + \
               '.csv'
    f_fr = open(feedback_report_filename, "a", encoding="utf-16")

    f_ar.write('Информация о пользователях\n')
    f_ar.write('№; UserId; UserPhone; Authorization; Company; Location; '
               'Number of requests for all lots; '
               'Number of requests for nearby lots; '
               'Number of requests for full lot info; '
               'Number of tries to set blitz rate\n')

    for i, user in enumerate(list(_USERS)):
        f_ar.write(str(i + 1) + '; ' +
                   user + '; ' +
                   str(_USERS[user]['PhoneNumber']) + '; ' +
                   str(_USERS[user]['Login']) + '; ' +
                   str(_USERS[user]['CompanyName']) + '; ' +
                   str(_USERS[user]['LastLocation']['Latitude']) + ', ' +
                   str(_USERS[user]['LastLocation']['Longitude']) + '; ' +
                   str(_USERS[user]['GetAllLotsTries']) + '; ' +
                   str(_USERS[user]['GetNearbyLotsTries']) + '; ' +
                   str(len(_USERS[user]['GetFullLotInfoTries'])) + '; ' +
                   str(len(_USERS[user]['SetBlitzRateTries'])) + '\n')

    f_ar.write('\n'*3)
    f_ar.write('Информация о действиях с лотами\n')
    f_ar.write('№; UserId; UserPhone; Operation; Lot; RouteStart; RouteEnd; StartLocation; EndLocation; BlitzRate\n')

    f_fr.write('Обратная связь\n')
    f_fr.write('№; UserId; UserPhone; Company; Feedback\n')

    i = 0
    j = 0
    for user in list(_USERS):
        for lot in list(_USERS[user]['GetFullLotInfoTries']):

            lot = atlas.get_lot(lot_id=lot)

            if lot is not None:
                lot_name = lot['Routes'][0]['Name']
                lot_start_location = lot['Path']['Start']['LocationName']
                if 'FullAddress' in lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']:
                    lot_end_location = lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']['FullAddress']
                else:
                    lot_end_location = ''
                route_start_time = date_shift(lot['Path']['Start']['ArrivalTime'], TIME_OFFSET)
                route_end_time = date_shift(lot['Path']['End']['ArrivalTime'], TIME_OFFSET)
                lot_blitz_rate = None
                if 'BlitzBetPrice' in lot['LotInfo']:
                    lot_blitz_rate = lot['LotInfo']['BlitzBetPrice']

                i += 1
                f_ar.write(str(i) + '; ' +
                           user + '; ' +
                           str(_USERS[user]['PhoneNumber']) + '; ' +
                           'Looked' + '; ' +
                           lot_name + '; ' +
                           route_start_time + '; ' +
                           route_end_time + '; ' +
                           lot_start_location + '; ' +
                           lot_end_location + '; ' +
                           str(lot_blitz_rate) + '\n')

        for lot in list(_USERS[user]['SetBlitzRateTries']):

            lot = atlas.get_lot(lot_id=lot)

            if lot is not None:
                lot_name = lot['Routes'][0]['Name']
                lot_start_location = lot['Path']['Start']['LocationName']
                if 'FullAddress' in lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']:
                    lot_end_location = lot['Routes'][0]['DeliveryRoutePoints'][0]['AddressInfo']['FullAddress']
                else:
                    lot_end_location = ''
                route_start_time = date_shift(lot['Path']['Start']['ArrivalTime'], TIME_OFFSET)
                route_end_time = date_shift(lot['Path']['End']['ArrivalTime'], TIME_OFFSET)
                lot_blitz_rate = None
                if 'BlitzBetPrice' in lot['LotInfo']:
                    lot_blitz_rate = lot['LotInfo']['BlitzBetPrice']

                i += 1
                f_ar.write(str(i) + '; ' +
                           user + '; ' +
                           str(_USERS[user]['PhoneNumber']) + '; ' +
                           'Picked up' + '; ' +
                           lot_name + '; ' +
                           route_start_time + '; ' +
                           route_end_time + '; ' +
                           lot_start_location + '; ' +
                           lot_end_location + '; ' +
                           str(lot_blitz_rate) + '\n')

        if 'Feedbacks' in _USERS[user]:
            for feedback in list(_USERS[user]['Feedbacks']):

                j += 1
                f_fr.write(str(j) + '; ' +
                           user + '; ' +
                           str(_USERS[user]['PhoneNumber']) + '; ' +
                           str(_USERS[user]['CompanyName']) + '; ' +
                           feedback + '\n')

    f_ar.close()
    f_fr.close()

    current_time = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")

    telegram_bot.send_document(chat_id=chat_id,  # id чата пользователя
                               data=open(advanced_report_filename, 'rb'),  # файл
                               parse_mode='Markdown',  # тип разметки сообщения
                               reply_markup=main_markup2(chat_id=chat_id))  # формат меню

    telegram_bot.send_document(chat_id=chat_id,  # id чата пользователя
                               data=open(feedback_report_filename, 'rb'),  # файл
                               parse_mode='Markdown',  # тип разметки сообщения
                               reply_markup=main_markup2(chat_id=chat_id))  # формат меню

    telegram_bot.send_document(chat_id=chat_id,  # id чата пользователя
                               data=open(USERS_DATA_FILE, 'rb'),  # файл
                               parse_mode='Markdown',  # тип разметки сообщения
                               reply_markup=main_markup2(chat_id=chat_id))  # формат меню

    print("{} - bot answered into {} chat: {}".format(current_time, chat_type, chat_id))


# Отправка отчётности
def send_report(chat_type: str, chat_id: str):
    logging.info('User {} tried to request report'.format(chat_id))

    message = '*Отчёт:*\n • уникальных пользователей: ' + str(len(_USERS.keys())) + '\n'

    phone_numbers = 0
    authorized_users = 0
    get_all_lot_tries = 0
    get_nearby_lots_tries = 0
    get_full_lot_info_tries = 0
    set_blitz_rate_tries = 0
    for user in list(_USERS):
        if _USERS[user]['PhoneNumber'] is not None:
            phone_numbers += 1
        if _USERS[user]['Login']:
            authorized_users += 1
        if _USERS[user]['GetAllLotsTries'] > 0:
            get_all_lot_tries += _USERS[user]['GetAllLotsTries']
        if _USERS[user]['GetNearbyLotsTries'] > 0:
            get_nearby_lots_tries += _USERS[user]['GetNearbyLotsTries']
        if len(_USERS[user]['GetFullLotInfoTries']) > 0:
            get_full_lot_info_tries += len(_USERS[user]['GetFullLotInfoTries'])
        if len(_USERS[user]['SetBlitzRateTries']) > 0:
            set_blitz_rate_tries += len(_USERS[user]['SetBlitzRateTries'])

    message += ' • пользователей c номером телефона: ' + str(phone_numbers) + '\n' \
               ' • авторизованных пользователей: ' + str(authorized_users) + '\n' \
               ' • запросов всех лотов: ' + str(get_all_lot_tries) + '\n' \
               ' • запросов ближайших лотов: ' + str(get_nearby_lots_tries) + '\n' \
               ' • запросов информации о лоте: ' + str(get_full_lot_info_tries) + '\n' \
               ' • нажатий на блиц-ставку: ' + str(set_blitz_rate_tries) + '\n'

    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                 reply_markup=main_markup2(chat_id=chat_id))

    send_advanced_report(chat_type, chat_id)


# Запрос обратной связи
def get_feedback(chat_type: str, chat_id: str):
    logging.info('User {} tried to create feedback'.format(chat_id))

    if _USERS[chat_id]['Login'] and _USERS[chat_id]['PhoneNumber'] is not None:
        user_phone_number = _USERS[chat_id]['PhoneNumber']
        if check_user_by_number(chat_id=chat_id, phone_number=user_phone_number) or True:
            _USERS[chat_id]['FeedbackCreating'] = True
            message = 'Пожалуйста, оставьте свой отзыв\n'
            reply_markup = cancel_feedback_message_markup()

        else:
            _USERS[chat_id]['Login'] = False
            message = 'Вы не авторизованы.\nДля авторизации нажмите на кнопку «*Авторизоваться*» в главном меню.'
            reply_markup = main_markup2(chat_id=chat_id)
    else:
        message = 'Вы не авторизованы.\nДля авторизации нажмите на кнопку «*Авторизоваться*» в главном меню.'
        reply_markup = main_markup2(chat_id=chat_id)

    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                 reply_markup=reply_markup)


# Создание обратной связи
def create_feedback(chat_type: str, chat_id: str, feedback_text: str):
    logging.info('User {} created feedback'.format(chat_id))

    if 'Feedbacks' not in _USERS[chat_id]:
        _USERS[chat_id]['Feedbacks'] = []

    _USERS[chat_id]['Feedbacks'].append(feedback_text)

    message = 'Спасибо за обратную связь!'

    send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                 reply_markup=main_markup2(chat_id=chat_id))


# Проверка наличия номера телефона пользователя в базе Atlas
def check_user_by_number(chat_id: str, phone_number: str):
    role = 'RoutesBiddingCompetitor'

    users = atlas.get_users_from_moloch()

    if users is not None and len(users) > 0:
        for user in users:
            if 'Phone' in user and 'Roles' in user and 'CompanyId' in user:
                if user['Phone'] == phone_number:
                    carrier = atlas.get_carrier(carrier_id=user['CompanyId'])
                    if role in user['Roles'] and carrier is not None:
                        _USERS[chat_id]['CompanyId'] = user['CompanyId']
                        if 'Name' in carrier:
                            _USERS[chat_id]['CompanyName'] = carrier['Name']
                        return True
    return False


# Переавторизация в Atlas
def reauth_atlas(chat_type: str, chat_id: str):
    atlas.stop_client()
    atlas.start_client()
    if atlas.user_token != '':
        message = 'Authorization in Atlas is done'
        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))


def save_new_user(chat_id: str):
    _USERS[chat_id] = {
        "PhoneNumber": None,
        "Login": False,
        "CompanyId": '',
        "CompanyName": '',
        "GetAllLotsTries": 0,
        "GetNearbyLotsTries": 0,
        "LastLocation": {
            "Latitude": None,
            "Longitude": None
        },
        "GetFullLotInfoTries": [],
        "SetBlitzRateTries": [],
        "RadiusRequesting": False,
        "FeedbackCreating": False,
        "Feedbacks": []
    }


"""
Commands for bot
"""
commands = {
    "Admin": {
        "health check": send_sign_of_life,
        "показать все рейсы": send_lots,
        "помощь": send_help_info,
        "отчёт": send_report,
        "reauth in atlas": reauth_atlas,
        "обратная связь": get_feedback
    },
    "User": {
        "health check": send_sign_of_life,
        "показать все рейсы": send_lots,
        "помощь": send_help_info,
        "обратная связь": get_feedback
    }
}


@telegram_bot.message_handler(func=lambda message: True and message.content_type == 'text')
def main(message):
    chat_id = str(message.chat.id)
    chat_type = str(message.chat.type)
    message_text = str(message.text).lower()

    if chat_id not in _USERS:
        save_new_user(chat_id=chat_id)

    # users_data = get_data(USERS_DATA_FILE)
    # if chat_id not in users_data:
    #     users_data[chat_id] = {"Login": None, "Password": None, "Token": None}
    #     save_to_json(json_file_path=USERS_DATA_FILE, data=users_data)

    if message_text in commands['Admin'].keys() or message_text in commands['User'].keys():

        _USERS[chat_id]['RadiusRequesting'] = False
        _USERS[chat_id]['FeedbackCreating'] = False

        if str(chat_id) in private_chat_id:
            commands['Admin'].get(message_text)(chat_type, chat_id)
        else:
            commands['User'].get(message_text)(chat_type, chat_id)
    else:
        if 'RadiusRequesting' in _USERS[chat_id] and _USERS[chat_id]['RadiusRequesting']:
            if message.text.isdigit() and 1 <= int(message.text) <= MAX_RADIUS:
                _USERS[chat_id]['RadiusRequesting'] = False
                latitude = _USERS[chat_id]['LastLocation']['Latitude']
                longitude = _USERS[chat_id]['LastLocation']['Longitude']
                send_nearby_lots(chat_type=chat_type, chat_id=chat_id,
                                 latitude=latitude, longitude=longitude,
                                 radius=int(message.text))
            else:
                message = 'Пожалуйста, введите значение радиуса (км.) зоны поиска рейсов в виде числа от 1 до ' \
                          + str(MAX_RADIUS) + '\n'
                send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                             reply_markup=cancel_radius_message_markup())

        elif 'FeedbackCreating' in _USERS[chat_id] and _USERS[chat_id]['FeedbackCreating']:
            _USERS[chat_id]['FeedbackCreating'] = False
            create_feedback(chat_type=chat_type, chat_id=chat_id, feedback_text=message_text)

        else:
            send_start_message(chat_type=chat_type, chat_id=chat_id)

        # elif '/login' in message_text:
        #     users_data = get_data(USERS_DATA_FILE)
        #     users_data[chat_id]['Login'] = message_text.split(' ')[1]
        #     save_to_json(json_file_path=USERS_DATA_FILE, data=users_data)
        #     telegram_bot.send_message(chat_id=chat_id, text='Укажите пароль.\nОтправьте: /pass пароль')
        # elif '/pass' in message_text:
        #     users_data = get_data(USERS_DATA_FILE)
        #     if users_data[chat_id]['Login'] is not None:
        #         users_data[chat_id]['Password'] = message_text.split(' ')[1]
        #         save_to_json(json_file_path=USERS_DATA_FILE, data=users_data)
        #         user_token = get_user_token(username=users_data[chat_id]['Login'],
        #                                     password=users_data[chat_id]['Password'])
        #         if user_token is not None:
        #             users_data[chat_id]['Token'] = user_token
        #             save_to_json(json_file_path=USERS_DATA_FILE, data=users_data)
        #         else:
        #             telegram_bot.send_message(chat_id=chat_id,
        #                                       text='Неверный логин или пароль. Укажите логин.\nОтправьте: /login логин')
        #     else:
        #         telegram_bot.send_message(chat_id=chat_id, text='Укажите логин.\nОтправьте: /login логин')

    # else:  # TODO Потом включить
    #     if message_text in commands['User'].keys():
    #         commands['User'].get(message_text)(chat_type, chat_id)
    #     else:
    #         send_start_message(chat_type, chat_id)


@telegram_bot.message_handler(content_types=["location"])
def location(message):
    chat_id = str(message.chat.id)
    chat_type = str(message.chat.type)

    if chat_id not in _USERS:
        save_new_user(chat_id=chat_id)

    _USERS[chat_id]['RadiusRequesting'] = False
    _USERS[chat_id]['FeedbackCreating'] = False

    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        logging.info('User {} tried to request nearby lots for location ({},{})'.format(chat_id, latitude, longitude))
        _USERS[chat_id]['LastLocation']['Latitude'] = latitude
        _USERS[chat_id]['LastLocation']['Longitude'] = longitude

        _USERS[chat_id]['RadiusRequesting'] = True
        message = 'Пожалуйста, введите значение радиуса (км.) зоны поиска рейсов в виде числа от 1 до ' \
                  + str(MAX_RADIUS) + '\n'
        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=cancel_radius_message_markup())


@telegram_bot.message_handler(content_types=["contact"])
def contact(message):
    chat_id = str(message.chat.id)
    chat_type = str(message.chat.type)
    logging.info('User {} logged in'.format(chat_id))

    if chat_id not in _USERS:
        save_new_user(chat_id=chat_id)

    _USERS[chat_id]['RadiusRequesting'] = False
    _USERS[chat_id]['FeedbackCreating'] = False

    if message.contact is not None and message.contact.phone_number is not None:

        if '+' in message.contact.phone_number:
            phone_number = message.contact.phone_number
        else:
            phone_number = '+' + message.contact.phone_number

        print(phone_number)
        _USERS[chat_id]['PhoneNumber'] = phone_number

        message = 'Проверяю наличие номера в базе. Пожалуйста подождите.'
        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))

        if check_user_by_number(chat_id=chat_id, phone_number=phone_number):
            _USERS[chat_id]['Login'] = True
            message = 'Вы успешно авторизовались по номеру ' + phone_number + '.'
        else:
            message = 'Не удалось авторизоваться.\n\n' \
                      'На платформе Atlas Chain не найден пользователь с номером ' + phone_number + ' и разрешением ' \
                      'на выставление блиц-ставки. Для подключения к платформе Atlas Chain перейдите по [ссылке]' \
                      '(https://atlaschain.ru/it-carriers/?utm_source=TelegramBot) и оставьте запрос на подключение.'

        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))
    else:
        message = 'Не удалось авторизоваться. Попробуйте ещё раз'
        send_message(chat_id=chat_id, chat_type=chat_type, message=message, parse_mode='Markdown',
                     reply_markup=main_markup2(chat_id=chat_id))


@telegram_bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_type = str(call.message.chat.type)
    chat_id = str(call.message.chat.id)
    message_id = str(call.message.message_id)

    # users_data = get_data(USERS_DATA_FILE)
    # if chat_id not in users_data:
    #     users_data[chat_id] = {"Login": None, "Password": None, "Token": None}
    #     save_to_json(json_file_path=USERS_DATA_FILE, data=users_data)

    if chat_id not in _USERS:
        save_new_user(chat_id=chat_id)

    _USERS[chat_id]['RadiusRequesting'] = False
    _USERS[chat_id]['FeedbackCreating'] = False

    if True:  # chat_id in private_chat_id:  # TODO Потом убрать
        if call.data == "cb_radius_cancel":
            telegram_bot.answer_callback_query(call.id, "Отменяю запрос радиуса зоны...")
            logging.info('User {} tried to cancel searching lots'.format(chat_id))
            _USERS[chat_id]['RadiusRequesting'] = False
            message_text = 'Запрос ближайших рейсов отменён'
            send_message(chat_id=chat_id, chat_type=chat_type, message=message_text, parse_mode='Markdown',
                         reply_markup=main_markup2(chat_id=chat_id))

        elif call.data == "cb_feedback_cancel":
            telegram_bot.answer_callback_query(call.id, "Отменяю отправку обратной связи...")
            logging.info('User {} tried to create feedback'.format(chat_id))
            _USERS[chat_id]['FeedbackCreating'] = False
            message_text = 'Если захотите снова оставить обратную связь, то нажмите на «*Обратная связь*»'
            send_message(chat_id=chat_id, chat_type=chat_type, message=message_text, parse_mode='Markdown',
                         reply_markup=main_markup2(chat_id=chat_id))

        elif call.data == "cb_get_lots":
            telegram_bot.answer_callback_query(call.id, "Запрашиваю доступные рейсы...")
            logging.info('User {} tried to request all lots'.format(chat_id))
            send_lots(chat_type=chat_type, chat_id=chat_id)
        elif call.data == "cb_help":
            logging.info('User {} tried to request help info'.format(chat_id))
            send_help_info(chat_type=chat_type, chat_id=chat_id)
        elif 'cb_blitz_' in call.data:
            telegram_bot.answer_callback_query(call.id, "Забираю рейс...")
            logging.info('User {} tried to put the blitz rate for lot_id: {}'.format(chat_id, call.data.split('_')[2]))
            set_blitz_rate(chat_type=chat_type, chat_id=chat_id, lot_id=call.data.split('_')[2])
        # elif 'Lots' in USERS[chat_id] and call.data.split('_')[1] in USERS[chat_id]['Lots']:
        #     send_full_lot_info(chat_type=chat_type, chat_id=chat_id, lot_id=call.data.split('_')[1])
        elif 'cb_lot_' in call.data:
            logging.info('User {} tried to request full info for lot_id: {}'.format(chat_id, call.data.split('_')[2]))
            send_full_lot_info(chat_type=chat_type, chat_id=chat_id, lot_id=call.data.split('_')[2])
        # elif call.data == "cb_auth":
        #     users_data = get_data(USERS_DATA_FILE)
        #     if users_data[chat_id]['Login'] is None or users_data[chat_id]['Password'] is None:
        #         telegram_bot.send_message(chat_id=chat_id, text='Укажите логин.\nОтправьте: /login логин')
        #     else:
        #         user_token = get_user_token(username=users_data[chat_id]['Login'],
        #                                     password=users_data[chat_id]['Password'])
        #         if user_token is not None:
        #             users_data[chat_id]['Token'] = user_token
        #             telegram_bot.answer_callback_query(call.id, "Вы уже авторизованы...")
        #         else:
        #             telegram_bot.send_message(chat_id=chat_id, text='Укажите логин.\nОтправьте: /login логин')


if __name__ == '__main__':
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H-%M-%S")
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='log_' + now + '.log', level=logging.INFO)

    _USERS = get_data(USERS_DATA_FILE)
    while True:
        try:
            print("bot running...")
            telegram_bot.polling(none_stop=True)
            # telegram_bot.infinity_polling()  # polling(none_stop=True, timeout=50)
        except Exception as e:
            logging.error(e)
            time.sleep(5)
            print("Internet error!")
