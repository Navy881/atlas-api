
import datetime
import uuid
from pymongo import MongoClient
from bson.binary import CSHARP_LEGACY, UUID_SUBTYPE, PYTHON_LEGACY
from bson.codec_options import CodecOptions

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

'''
collection = db['DriverKarma']  # get collection DriverKarma

for obj in collection.find():
    print(obj)
    break

print('')


for obj in collection.find({"CarrierId": uuid.UUID("255d0c97-644b-ac45-a50a-a84d0073e254")}): # get obj by CerrierId
    print(obj)
    break
'''


# For UUID
bookings_collection = db.get_collection('Bookings', CodecOptions(uuid_representation=UUID_SUBTYPE))
booking_models = bookings_collection.find({'Model.RoutePointId': uuid.UUID('d70ca0be-4113-4814-b99f-f0ba52cafaab')})
for model in booking_models:
    print('Booking: ', model)

# For LUUID
orders_collection = db.get_collection('Order', CodecOptions(uuid_representation=CSHARP_LEGACY))
order_models = orders_collection.find({'_id': uuid.UUID('ee38a1cf-ca83-0c48-835e-a911005a801d')})
for model in order_models:
    print('Order: ', model)

'''
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
        # input('Press key...')
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
    start = datetime.datetime(2019, 4, 1)
    end = datetime.datetime(2019, 12, 1)

    bookings_collection = db['Bookings']
    routes_collection = db['Route']
    # routes_collection = db.get_collection('Route', CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE))
    print(bookings_collection.find({}).count())
    print(bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}}).count())

    total = 0
    self_pickup_count = 0
    auto_created_count = 0
    manual_created_count = 0

    while start != datetime.datetime(2019, 12, 1):
        self_pickup_count = 0
        auto_created_count = 0
        manual_created_count = 0

        end = start + datetime.timedelta(days=1)
        bookings_count = bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}}).count()
        bookings = bookings_collection.find({'Model.Interval.From': {'$gte': start, '$lt': end}})
        for booking in bookings:
            if booking['Model']['RoutePointId'] is None:
                self_pickup_count += 1
                print(booking['CreatedBy'])
            else:
                print(booking['CreatedBy'])

        print(start, bookings_count, self_pickup_count)
        start = start + datetime.timedelta(days=1)
    print(total)

'''
if __name__ == '__main__':
    try:
        print('\nRoutes')
        # get_assigning_info()
        print('\nLots')
        # get_lots()
        print('\nBookings')
        # get_bookings()
    except Exception as e:
        print(e)
