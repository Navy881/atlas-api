
import datetime
import numpy as np
from collections import OrderedDict

from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)

FROM = input('From date (YYYY-MM-DD): ')

PRICE_EVALUATION_WEIGHT = 0.4
KARMA_EVALUATION_WEIGHT = 0.6


def get_carrier_data(carriers_data, carrier_id):
    carrier_data = {}
    for carrier in carriers_data:
        if carrier['CarrierId'] == carrier_id:
            carrier_data = carrier
    return carrier_data


def get_carrier_group(carriers_group, carrier_id):
    group = ''
    for key in carriers_group.keys():
        if carriers_group[key]['CarrierId'] == carrier_id:
            group = key
    return group


def carrier_group_calculation(carriers_data):
    # Расчёт оценок цены, кармы и общей оценки перевозчика
    price_evaluation = {}
    karma_evaluation = {}
    carrier_evaluation = {}
    max_price = max(int(carrier['Price']) for carrier in carriers_data)
    for carrier in carriers_data:
        price_evaluation[carrier['CarrierId']] = (max_price - carrier['Price']) / max_price
        if 0 <= carrier['Karma'] < 20:
            karma_evaluation[carrier['CarrierId']] = 0
        elif 20 <= carrier['Karma'] < 40:
            karma_evaluation[carrier['CarrierId']] = 0.3
        elif 40 <= carrier['Karma'] < 60:
            karma_evaluation[carrier['CarrierId']] = 0.6
        elif carrier['Karma'] > 60:
            karma_evaluation[carrier['CarrierId']] = 1

        carrier_evaluation[carrier['CarrierId']] = price_evaluation[carrier['CarrierId']] * PRICE_EVALUATION_WEIGHT + \
                                                   karma_evaluation[carrier['CarrierId']] * KARMA_EVALUATION_WEIGHT

    # Расчёт порядка перевозчков
    carrier_order = {}
    carrier_evaluation_sort = sorted(carrier_evaluation.items(), key=lambda kv: kv[1], reverse=True)
    carrier_order_counter = 0
    for item in carrier_evaluation_sort:
        carrier_order_counter += 1
        carrier_order[item[0]] = carrier_order_counter

    # Расчёт групп перевозчиков
    carriers_group = {}
    carriers_in_group_col = {'A': 0, 'B': 0, 'C': 0}
    carrier_col = len(carrier_order)
    for carrier in carrier_order:
        if carrier_order[carrier] <= carrier_col/3+np.sign(carrier_col % 3):
            carriers_in_group_col['A'] += 1
            carriers_group['A' + str(carriers_in_group_col['A'])] = get_carrier_data(carriers_data, carrier)
        elif carrier_col/3+np.sign(carrier_col % 3) < carrier_order[carrier] <= carrier_col/3*2+np.sign(carrier_col % 3):
            carriers_in_group_col['B'] += 1
            carriers_group['B' + str(carriers_in_group_col['B'])] = get_carrier_data(carriers_data, carrier)
        elif carrier_order[carrier] > carrier_col/3*2+np.sign(carrier_col % 3):
            carriers_in_group_col['C'] += 1
            carriers_group['C' + str(carriers_in_group_col['C'])] = get_carrier_data(carriers_data, carrier)

    # Расчёт кол-ва мест в очереди для групп с порядком
    groups_places_col = {'A': 0, 'B': 0, 'C': 0}
    queue_size = 0
    for el in carriers_group.keys():
        queue_size += carriers_group[el]['TransportCount']
        if el[0] == 'A':
            groups_places_col['A'] += carriers_group[el]['TransportCount']
        elif el[0] == 'B':
            groups_places_col['B'] += carriers_group[el]['TransportCount']
        elif el[0] == 'C':
            groups_places_col['C'] += carriers_group[el]['TransportCount']

    return carriers_group, carriers_in_group_col, groups_places_col, queue_size


if __name__ == '__main__':
    try:
        filename = 'autoassigning_report_' + str(datetime.datetime.now()).split(' ')[0] + '.txt'
        f = open(filename, "a")

        report_for_data = {}

        atlas.start_client()
        legs = atlas.get_all_legs()

        for leg in legs:
            queues = atlas.get_carrier_queues(leg_id=leg['Id'])
            if len(queues) > 0:

                for weight in queues:
                    print('Плечо:', leg['StartPoint']['Zone']['Name'], '-', leg['EndPoint']['Zone']['Name'])
                    f.write('Плечо: ' + leg['StartPoint']['Zone']['Name'] + ' - ' + leg['EndPoint']['Zone']['Name'] +
                            '\n')
                    print('Грузоподъемность:', weight['WeightType'])
                    f.write('Грузоподъемность:' + str(weight['WeightType']) + '\n')
                    carrier_contracts = leg['Details']['Contracts']

                    carrier_infos = []
                    for contracts in carrier_contracts:
                        if contracts['WeightType'] == weight['WeightType']:
                            carrier_infos = contracts['CarrierInfos']

                    for queue in weight['Queues']:
                        queue_dict = {}
                        print('\nДата построения очереди:', queue['Interval']['To'].split('T')[0])
                        f.write('\nДата построения очереди:' + queue['Interval']['To'].split('T')[0])
                        carriers = queue['Carriers']
                        print('\n№; Вермя; (UTC); Маршрут; Группа; Перевозчик; Карма; Ставка')
                        f.write('\n№; Вермя; (UTC); Маршрут; Группа; Перевозчик; Карма; Ставка\n')

                        # Add Karma value in carriers info
                        for carrier in carriers:
                            for carrier_info in carrier_infos:
                               if carrier['Id'] == carrier_info['CarrierId']:
                                   carrier_info['Karma'] = carrier['Karma']

                        carriers_group, carriers_in_group_col, groups_places_col, queue_size = \
                            carrier_group_calculation(carrier_infos)

                        for carrier in carriers:
                            carrier_model = atlas.get_carrier(carrier_id=carrier['Id'])

                            carrier_price = None
                            for carrier_info in carrier_infos:
                                if carrier_info['CarrierId'] == carrier['Id']:
                                    carrier_price = carrier_info['Price']

                            allocations = carrier['Allocations']
                            for allocation in allocations:
                                route = atlas.get_route(allocation['RouteId'])

                                time = allocation['Audit']['CreatedOn'].split('Z')[0]
                                # if len(allocation['Audit']['CreatedOn'].split('Z')[0].split('T')[1]) == 16:
                                #     for i in range(15):
                                #         time += (allocation['Audit']['CreatedOn'].split('Z')[0].split('T')[1][i])
                                # else:
                                #     time = allocation['Audit']['CreatedOn'].split('Z')[0].split('T')[1]

                                if allocation['StateInfo']['State'] == 'Approved':
                                    data = route['RouteInfo']['Name'], carrier_model['Name'], carrier['Karma'], \
                                           carrier_price, get_carrier_group(carriers_group, carrier['Id'])
                                    queue_dict[time] = data

                        queue_dict = OrderedDict(sorted(queue_dict.items()))

                        for i, time in enumerate(queue_dict.keys()):
                            showing_time = time.split('T')[0] + ' ' + time.split('T')[1]
                            data = queue_dict[time]
                            if time.split('T')[0] > FROM:
                                message_1 = data[0] + '; ' + data[1] + '; ' + leg['StartPoint']['Zone']['Name'] + '-' \
                                            + leg['EndPoint']['Zone']['Name']
                                message_2 = str(i + 1) + '; ' + showing_time + '; ' + data[0] + '; ' + data[4] + '; ' +\
                                            data[1] + '; ' + str(int(data[2])) + '; ' + str(int(data[3]))

                                if time.split('T')[0] in report_for_data.keys():
                                    assigning_events = report_for_data[time.split('T')[0]]
                                    assigning_events.append(message_1)
                                else:
                                    report_for_data[time.split('T')[0]] = []
                                    assigning_events = report_for_data[time.split('T')[0]]
                                    assigning_events.append(message_1)

                                print(message_2)
                                f.write(message_2 + '\n')
                    print('=========================================\n')
                    f.write('=========================================\n\n')

        print('#####################################################\n')
        f.write('\n#####################################################\n')
        report_for_data = OrderedDict(sorted(report_for_data.items()))
        for data in report_for_data.keys():
            assigning_events = report_for_data[data]
            print(data, 'Кол-во назначений:', len(assigning_events))
            f.write('\n' + data + ' Кол-во назначений: ' + str(len(assigning_events)) + '\n')
            for i, event in enumerate(assigning_events):
                i += 1
                message = str(i) + '; ' + event
                print(message)
                f.write(message + '\n')
            print('=========================================\n')
            f.write('=========================================\n')

        f.close()
    except Exception as e:
        print(e)
