from datetime import datetime, timedelta
from AtlasApi import AtlasApiConnect
from pymongo import MongoClient
from bson.binary import CSHARP_LEGACY
from bson.codec_options import CodecOptions
import uuid

url = ''
username = ''
password = ''

atlas = AtlasApiConnect(url=url, username=username, password=password)

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

FROM = '2020-06-03'
TO = '2020-09-16'
COMPANY_ID = '6015ecb5-2b5d-4328-88e3-a9ed00d91535'

if __name__ == '__main__':
    try:
        start = datetime.strptime(FROM, '%Y-%m-%d')
        end = datetime.strptime(TO, '%Y-%m-%d')

        atlas.start_client()
        persons = atlas.get_all_persons()

        orders_collection = db.get_collection('Order', CodecOptions(uuid_representation=CSHARP_LEGACY))
        orders = orders_collection.find({'$and': [
            {'Order.Audit.CreatedOn': {'$gte': start, '$lt': end}},
            {'Order.StateInfo.State': 22},
            {'Order.CompanyInfo.CompanyId': uuid.UUID(COMPANY_ID)}
        ]})

        print(orders.count())
        i = 0
        for order in orders:
            if 'DeliveryTimeSlot' in order:
                for person in persons:
                    if order['DeliveryTimeSlot']['Audit']['Initiator'] == person['Id']:
                        i += 1
            if 'PickupTimeSlot' in order:
                for person in persons:
                    if order['PickupTimeSlot']['Audit']['Initiator'] == person['Id']:
                        i += 1

        print(f'Всего заказов: {str(orders.count())}\nВсего перенесённых заказов: {i}')

    except Exception as e:
        print(e)
