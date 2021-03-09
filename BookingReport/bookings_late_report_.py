
from datetime import datetime, timedelta
from AtlasApi import AtlasApiConnect
from pymongo import MongoClient
from bson.binary import CSHARP_LEGACY
from bson.codec_options import CodecOptions
import uuid

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)

MONGO_HOST = ""
MONGO_PORT = 0
MONGO_DB = ""
MONGO_USER = ""
MONGO_PASS = ""

# Connecting
client = MongoClient(MONGO_HOST, MONGO_PORT)
# Database selection
db = client[MONGO_DB]
# db = client.get_database(MONGO_DB, bson.codec_options.CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE))
# Authenticating
db.authenticate(MONGO_USER, MONGO_PASS)

HUB_ID = 'f4421f9e-5962-4c68-8049-a45600f36f4b'

FROM = input('From date (YYYY-MM-DD): ')

if __name__ == '__main__':
    try:
        filename = 'bookings_report_' + str(datetime.now()).split(' ')[0] + '.csv'
        f = open(filename, "a")

        atlas.start_client()

        cedrus_users = atlas.get_users_from_company(company_id=HUB_ID)
        cedrus_user_ids = []
        for cedrus_user in cedrus_users:
            cedrus_user_ids.append(cedrus_user['Id'])

        # gates = atlas.get_gates(hub_id=HUB_ID)
        # date_from = datetime.strptime(FROM, '%Y-%m-%d').date()
        # date_now = datetime.now().date()
        # datetime_from = str(date_from) + 'T21:00:00.000Z'
        # datetime_to = str(date_now + timedelta(days=1)) + 'T21:00:00.000Z'

        table_title = "Date; " \
                      "Route; " \
                      "Initiator; " \
                      "Planning period.To; " \
                      "Planning period.To; " \
                      "ReachedTheZone; " \
                      "ArrivalApproved; " \
                      "Arrived; " \
                      "ReadyForWorkStart; " \
                      "WorkStarted; " \
                      "WorkFinished; " \
                      "ReadyToLeave; " \
                      "Left\n"
        print(table_title)
        f.write(table_title)

        start = datetime.strptime(FROM, '%Y-%m-%d')
        end = datetime.now()

        routes_collection = db.get_collection('Route', CodecOptions(uuid_representation=CSHARP_LEGACY))

        bookings_collection = db.get_collection('Bookings', CodecOptions(uuid_representation=CSHARP_LEGACY))
        bookings = bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}})
        print(bookings.count())
        for booking in bookings:
            if booking['Model']['RoutePointId'] is not None:
                point_history = atlas.get_route_point_history(route_point_id=str(booking['Model']['RoutePointId']))
                route_point_id = str(booking['Model']['RoutePointId'])
                route = routes_collection.find({'Route.RoutePoints._id': uuid.UUID(route_point_id)})

                point_state_history = []
                initiator = str(booking['CreatedBy'])

                for history_event in point_history:
                    if 'StateInfo' in history_event.keys():
                        point_state_history.append({'State': history_event['StateInfo']['State'],
                                                    'CreatedOn': history_event['StateInfo']['Audit']['CreatedOn']})
                        # if history_event['StateInfo']['State'] == 'Created':
                        #     initiator = str(booking['CreatedBy'])

                    elif 'State' in history_event.keys():
                        point_state_history.append({'State': history_event['State'],
                                                    'CreatedOn': history_event['Audit']['CreatedOn']})

                reachedTheZone = ''
                arrivalApproved = ''
                arrived = ''
                readyForWorkStart = ''
                workStarted = ''
                workFinished = ''
                readyToLeave = ''
                left = ''

                for state in point_state_history:
                    state_created_on = str(datetime.strptime(state['CreatedOn'].split('.')[0], '%Y-%m-%dT%H:%M:%S'))
                    if 'ReachedTheZone' in state.values():
                        reachedTheZone = state_created_on
                    elif 'ArrivalApproved' in state.values():
                        arrivalApproved = state_created_on
                    elif 'Arrived' in state.values():
                        arrived = state_created_on
                    elif 'ReadyForWorkStart' in state.values():
                        readyForWorkStart = state_created_on
                    elif 'WorkStarted' in state.values():
                        workStarted = state_created_on
                    elif 'WorkFinished' in state.values():
                        workFinished = state_created_on
                    elif 'ReadyToLeave' in state.values():
                        readyToLeave = state_created_on
                    elif 'Left' in state.values():
                        left = state_created_on

                # route = atlas.get_route_by_route_point_id(route_point_id=str(booking['Model']['RoutePointId']))
                if route.count() > 0:
                    route_name = route[0]['Route']['RouteInfo']['Name']
                else:
                    route_name = ''

                if initiator in cedrus_user_ids:
                    initiator = 'CEDRUS'
                else:
                    initiator = 'Перевозчик'

                table_entry = f'{str(booking["Model"]["Interval"]["From"]).split(" ")[0]};' \
                              f'{route_name};' \
                              f'{initiator};' \
                              f'{booking["Model"]["Interval"]["From"]};' \
                              f'{booking["Model"]["Interval"]["To"]};' \
                              f'{reachedTheZone};' \
                              f'{arrivalApproved};' \
                              f'{arrived};' \
                              f'{readyForWorkStart};' \
                              f'{workStarted};' \
                              f'{workFinished};' \
                              f'{readyToLeave};' \
                              f'{left};' \
                              f'{booking["GateId"]}\n'

                print(table_entry)
                f.write(table_entry)

        f.close()
    except Exception as e:
        print(e)
