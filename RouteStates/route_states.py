
from datetime import datetime, timedelta
from AtlasApi import AtlasApiConnect
from pymongo import MongoClient
from bson.binary import CSHARP_LEGACY
from bson.codec_options import CodecOptions


url = ''
username = ''
password = ''
moloch = ''

MONGO_HOST = ""
MONGO_PORT = 0
MONGO_DB = ""
MONGO_USER = ""
MONGO_PASS = ""

atlas = AtlasApiConnect(url=url, moloch_url=moloch, username=username, password=password)


if __name__ == '__main__':
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        db.authenticate(MONGO_USER, MONGO_PASS)

        routes_collection = db.get_collection('Route', CodecOptions(uuid_representation=CSHARP_LEGACY))
        # routes = routes_collection.find({})

        start = datetime.strptime('2020-01-01', '%Y-%m-%d')
        end = datetime.now()
        routes = routes_collection.find({'CreatedOn': {'$gte': start, '$lt': end}})

        i = 0
        j = 0
        k = 0
        for route in routes:
            print('\n', route['_id'])
            time_2 = datetime.now()
            time_1 = datetime.now()
            if 'StateHistory' in route:
                for state_event in route['StateHistory']:

                    if state_event['State'] == 4:
                        print(state_event['State'], state_event['Audit']['CreatedOn'])
                        time_1 = datetime.strptime(str(state_event['Audit']['CreatedOn']).split('.')[0], '%Y-%m-%d %H:%M:%S')
                    elif state_event['State'] == 7:
                        k += 1
                        print(state_event['State'], state_event['Audit']['CreatedOn'])
                    elif state_event['State'] == 11:
                        print(state_event['State'], state_event['Audit']['CreatedOn'])
                        time_2 = datetime.strptime(str(state_event['Audit']['CreatedOn']).split('.')[0], '%Y-%m-%d %H:%M:%S')
            if time_2 > time_1:
                i += 1
                print(time_2 - time_1)
                if time_2 - time_1 > timedelta(hours=1):
                    j += 1

        print(routes.count())
        print(i)
        print(j)
        print(k)


        '''
        atlas.start_client()
        routes = atlas.get_all_route()
        print(len(routes))
        for route in routes:

            route_history = atlas.get_route_history(route['Id'])
            for event in route_history:
                if 'StateInfo' in event:
                    if event['StateInfo']['State'] == 'CarrierAssigned':
                        print(route['Id'])
                        print(event['StateInfo']['State'], event['StateInfo']['Audit']['CreatedOn'])
                    elif event['StateInfo']['State'] == 'CarrierAccepted':
                        print(event['StateInfo']['State'], event['StateInfo']['Audit']['CreatedOn'])
                    elif event['StateInfo']['State'] == 'PerformerAssigned':
                        print(event['StateInfo']['State'], event['StateInfo']['Audit']['CreatedOn'])
            # input('next...')
        '''
    except Exception as e:
        print(e)
