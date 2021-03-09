
from pymongo import MongoClient
import datetime
from AtlasApi import AtlasApiConnect

CEDRUS_ID = 'f4421f9e-5962-4c68-8049-a45600f36f4b'

MONGO_HOST = ""
MONGO_PORT = 0
MONGO_DB = ""
MONGO_USER = ""
MONGO_PASS = ""

# Connecting
client = MongoClient(MONGO_HOST, MONGO_PORT)
# Database selection
db = client[MONGO_DB]
# Authenticating
db.authenticate(MONGO_USER, MONGO_PASS)

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)


def get_assigning_info():
    start = datetime.datetime(2019, 10, 1)
    end = datetime.datetime(2019, 12, 1)

    collection = db['Route']
    print(collection.find({}).count())
    print(collection.find({"Route.CarrierInfo.Audit.CreatedOn": {'$gte': start, '$lt': end}}).count())
    total = 0
    while start != datetime.datetime(2019, 12, 1):
        end = start + datetime.timedelta(days=1)
        count = collection.find({"Route.CarrierInfo.Audit.CreatedOn": {'$gte': start, '$lt': end}}).count()
        total += count
        print(start, count)
        #input('Press key...')
        start = start + datetime.timedelta(days=1)
    print(total)

    # for item in collection.find({}):
    #     print(item['Route']['Audit']['CreatedOn'])


    # print(collection.find({"OrderEvents.EventType": 1}).count())


def get_lots():
    start = datetime.datetime(2019, 10, 1)
    end = datetime.datetime(2019, 12, 1)

    collection = db['BiddingLots']
    print(collection.find({}).count())
    print(collection.find({'BiddingLot.StateInfo.State': 4,
                           'BiddingLot.StateInfo.StateType': 1,
                           "BiddingLot.Audit.CreatedOn": {'$gte': start, '$lt': end}}).count())
    total = 0
    while start != datetime.datetime(2019, 12, 1):
        end = start + datetime.timedelta(days=1)
        lot_count = collection.find({'BiddingLot.StateInfo.State': 4,
                                     'BiddingLot.StateInfo.StateType': 1,
                                     "BiddingLot.Audit.CreatedOn": {'$gte': start, '$lt': end}}).count()
        total += lot_count
        print(start, lot_count)
        start = start + datetime.timedelta(days=1)
    print(total)


def get_bookings():

    atlas.start_client()
    cedrus_users = atlas.get_users_from_company(company_id=CEDRUS_ID)

    cedrus_user_ids = []
    for cedrus_user in cedrus_users:
        cedrus_user_ids.append(cedrus_user['Id'])

    start = datetime.datetime(2019, 4, 1)
    end = datetime.datetime(2019, 12, 1)

    bookings_collection = db['Bookings']
    routes_collection = db['Route']
    # routes_collection = db.get_collection('Route', CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE))
    print(bookings_collection.find({}).count())
    print(bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}}).count())

    total = 0

    while start != datetime.datetime(2019, 12, 1):
        total_count = 0
        self_pickup_count = 0
        auto_created_count = 0
        manual_created_count = 0

        end = start + datetime.timedelta(days=1)
        bookings_count = bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}}).count()
        bookings = bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}})
        for booking in bookings:
            if booking['Model']['RoutePointId'] is None:
                self_pickup_count += 1
            else:
                if str(booking['CreatedBy']) in cedrus_user_ids:
                    manual_created_count += 1
                else:
                    auto_created_count += 1
            total_count = self_pickup_count + manual_created_count + auto_created_count
        print(start, bookings_count,
              ';Total:;', total_count,
              ';Auto:;', auto_created_count,
              ';Manual:;', manual_created_count,
              ';Self:;', self_pickup_count)
        total += bookings_count
        start = start + datetime.timedelta(days=1)
    print(total)


if __name__ == '__main__':
    try:
        print('\nRoutes')
        # get_assigning_info()
        print('\nLots')
        # get_lots()
        print('\nBookings')
        get_bookings()
    except Exception as e:
        print(e)