
import datetime
import numpy as np

from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)

FROM = input('From date (YYYY-MM-DD): ')

PRICE_EVALUATION_WEIGHT = 0.4
KARMA_EVALUATION_WEIGHT = 0.6
SKIP_COUNT_TO_QUEUE = 5
LOAD_UNLOAD_TYPES = {}
ZONE_RESTRICTIONS = {}


def get_restriction_title(type_value):
    result = ''
    for elem in LOAD_UNLOAD_TYPES:
        if elem['LoadUnloadType'] == type_value:
            result = elem['Title']
    for elem in ZONE_RESTRICTIONS:
        if elem['ZoneRestriction'] == type_value:
            result = elem['Title']
    return result


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
    carriers_name_karma = {}
    carriers_name_id = {}

    for carrier in carriers_data:
        carrier_model = atlas.get_carrier(carrier_id=carrier['CarrierId'])
        if carrier_model is not None:
            carrier_name = carrier_model['Name'].lower()
        else:
            carrier_name = carrier['CarrierId']
        carriers_name_id[carrier_name] = carrier['CarrierId']
        carriers_name_karma[carrier_name] = carrier['Karma']

    # Расчёт порядка перевозчков
    carrier_order = {}
    # Сортировка по наименованию
    carrier_evaluation_sort = sorted(carriers_name_karma.items(), key=lambda kv: kv[0], reverse=False)
    carriers_name_karma = {}
    for item in carrier_evaluation_sort:
        carriers_name_karma[item[0]] = item[1]
    # Сортировка по значению кармы
    carrier_evaluation_sort = sorted(carriers_name_karma.items(), key=lambda kv: kv[1], reverse=True)

    carrier_order_counter = 0
    for item in carrier_evaluation_sort:
        carrier_order_counter += 1
        carrier_order[carriers_name_id[item[0]]] = carrier_order_counter

    # Расчёт групп перевозчиков
    carriers_group = {}
    carriers_in_group_col = {'A': 0, 'B': 0, 'C': 0}
    carrier_col = len(carrier_order)
    for carrier in carrier_order:
        if carrier_order[carrier] <= carrier_col / 3 + np.sign(carrier_col % 3):
            carriers_in_group_col['A'] += 1
            carriers_group['A' + str(carriers_in_group_col['A'])] = get_carrier_data(carriers_data, carrier)
        elif carrier_col / 3 + np.sign(carrier_col % 3) < carrier_order[carrier] <= carrier_col / 3 * 2 + np.sign(
                carrier_col % 3):
            carriers_in_group_col['B'] += 1
            carriers_group['B' + str(carriers_in_group_col['B'])] = get_carrier_data(carriers_data, carrier)
        elif carrier_order[carrier] > carrier_col / 3 * 2 + np.sign(carrier_col % 3):
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


def print_report(leg_queues):
    filename = 'autoassigning_report_' + str(datetime.datetime.now()).split(' ')[0] + '.csv'
    f = open(filename, "a")

    for leg in leg_queues:
        f.write(leg + '\n\n')
        for weight in leg_queues[leg]:
            f.write('Грузоподъемность: ' + weight + '\n\n')
            for queue in leg_queues[leg][weight]:
                queue_name = list(queue)[0]
                f.write(queue_name + '\n')
                f.write('№; Вермя; (UTC); Маршрут; Группа; Перевозчик; Карма; Ставка; Использованные ограничения\n')
                for assignment in queue[queue_name]:
                    f.write(assignment + '\n')
                f.write('\n')
        f.write('=========================================\n\n')
    f.close()


def get_queue_assignments():
    global LOAD_UNLOAD_TYPES, ZONE_RESTRICTIONS

    leg_queues = {}
    atlas.start_client()
    legs = atlas.get_all_legs()
    weight_types = atlas.get_weight_types_dictionary()
    LOAD_UNLOAD_TYPES = atlas.get_load_unload_types()
    ZONE_RESTRICTIONS = atlas.get_zone_restrictions()

    for i, leg in enumerate(legs):
        if 'ExternalId' in leg: # and leg['ExternalId'] == 'stop':
            leg_weights = {}

            print(i, '/', len(legs), 'Плечо:', leg['ExternalId'], leg['StartPoint']['Zone']['Name'],
                  '-', leg['EndPoint']['Zone']['Name'], leg['Id'])
            leg_info = 'Плечо: ' + leg['ExternalId'] + ' ' + \
                       leg['StartPoint']['Zone']['Name'] + ' - ' + leg['EndPoint']['Zone']['Name']

            for weight_type in weight_types:
                leg_weight_queues = []
                weight_type = weight_type['WeightType']
                skip_count = 0
                while skip_count >= 0:
                    queues = atlas.get_carrier_queues(leg_id=leg['Id'],
                                                      weight_type=str(weight_type),
                                                      skip_count=skip_count)
                    if len(queues) > 0:
                        carrier_contracts = leg['Details']['Contracts']
                        carrier_infos = []
                        for contracts in carrier_contracts:
                            if contracts['WeightType'] == weight_type:
                                carrier_infos = contracts['CarrierInfos']

                        for queue in queues:
                            assignments = []
                            queue_dict = {}
                            queue_info = 'Дата построения очереди: ' + queue['Interval']['To'].split('T')[0]

                            # Add Karma value in carriers info
                            queue_configuration = queue['Configuration']
                            for carrier in queue_configuration:
                                for carrier_info in carrier_infos:
                                    if carrier['CarrierId'] == carrier_info['CarrierId']:
                                        carrier_info['Karma'] = carrier['Karma']
                                    else:
                                        carrier_info['Karma'] = 100

                            carriers_group, carriers_in_group_col, groups_places_col, queue_size = \
                                carrier_group_calculation(carrier_infos)

                            allocations = queue['Allocations']

                            for allocation in allocations:
                                if allocation['StateInfo']['State'] == 'Approved':
                                    time = allocation['Audit']['CreatedOn'].split('Z')[0]
                                    if time.split('T')[0] > FROM:
                                        carrier_model = atlas.get_carrier(carrier_id=allocation['CarrierId'])
                                        route_model = atlas.get_route(route_id=allocation['RouteId'])

                                        carrier_karma = None
                                        for carrier in queue_configuration:
                                            if allocation['CarrierId'] == carrier['CarrierId']:
                                                carrier_karma = carrier['Karma']

                                        carrier_restrictions = ''
                                        transport_restrictions = allocation['UsedRestrictions']
                                        if transport_restrictions is not None:
                                            for restrictions in transport_restrictions:
                                                if transport_restrictions[restrictions] is not None:
                                                    for restriction in transport_restrictions[restrictions]:
                                                        restriction_title = get_restriction_title(list(restriction.values())[0])
                                                        carrier_restrictions += '"' + restriction_title + '" '

                                        carrier_price = None
                                        for carrier_info in carrier_infos:
                                            if carrier_info['CarrierId'] == allocation['CarrierId']:
                                                carrier_price = carrier_info['Price']

                                        if carrier_model is not None:
                                            carrier_name = carrier_model['Name']
                                        else:
                                            carrier_name = allocation['CarrierId']

                                        if route_model is not None and 'RouteInfo' in route_model:
                                            route_name = route_model['RouteInfo']['Name']
                                        else:
                                            route_name = allocation['RouteId']

                                        data = route_name, \
                                               carrier_name, \
                                               carrier_karma, \
                                               get_carrier_group(carriers_group, allocation['CarrierId']), \
                                               carrier_restrictions

                                        queue_dict[time] = data

                            for j, time in enumerate(queue_dict.keys()):
                                showing_time = time.split('T')[0] + ' ' + time.split('T')[1].split('.')[0]
                                data = queue_dict[time]
                                if time.split('T')[0] > FROM:
                                    message_2 = str(j + 1) + '; ' + \
                                                showing_time + '; ' + \
                                                data[0] + '; ' + \
                                                data[3] + '; ' + \
                                                data[1] + '; ' + \
                                                str(int(data[2])) + '; ' + \
                                                data[4]

                                    assignments.append(message_2)
                            if len(assignments) > 0:
                                leg_weight_queues.append({queue_info: assignments})
                        skip_count += SKIP_COUNT_TO_QUEUE
                    else:
                        skip_count = -1

                if len(leg_weight_queues) > 0:
                    leg_weights[str(weight_type)] = leg_weight_queues
            if len(leg_weights.keys()) > 0:
                leg_queues[leg_info] = leg_weights
    print_report(leg_queues)


if __name__ == '__main__':
    try:
        get_queue_assignments()
        atlas.stop_client()
    except Exception as e:
        print(e)
