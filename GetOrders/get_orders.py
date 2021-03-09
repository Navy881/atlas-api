
import datetime
import uuid
from pymongo import MongoClient
from bson.binary import CSHARP_LEGACY, UUID_SUBTYPE, PYTHON_LEGACY
from bson.codec_options import CodecOptions

from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''

MONGO_HOST = ""
MONGO_PORT = 0
MONGO_DB = ""
MONGO_USER = ""
MONGO_PASS = ""

COMPANY_ID = "4b5de9c1-3117-4f57-996d-a9a600bcd4c8"

# Connecting
client = MongoClient(MONGO_HOST, MONGO_PORT)
# Database selection
db = client[MONGO_DB]
# Authenticating
db.authenticate(MONGO_USER, MONGO_PASS)

atlas = AtlasApiConnect(url=stand, username=username, password=password)


def get_orders_by_company():
    filename = 'orders' + str(datetime.datetime.now()).split(' ')[0] + '.csv'
    f = open(filename, "a")

    start = datetime.datetime(2020, 6, 1)
    end = datetime.datetime(2020, 8, 1)

    atlas.start_client()
    carriers = {}
    carriers_models = atlas.get_all_carriers()
    for carrier in carriers_models:
        carriers[carrier['Id']] = carrier['Name']

    orders_collection = db.get_collection('Order', CodecOptions(uuid_representation=CSHARP_LEGACY))
    # print(orders_collection.find({}).count())
    order_models = orders_collection.find({"Order.CompanyInfo.CompanyId": uuid.UUID(COMPANY_ID),
                                           "Order.DeliveryTimeSlot.To": {'$gte': start, '$lt': end}})
    print(order_models.count())

    orders = "CreatedOn; Number; Delivery Timeslot to; Carrier; Completed; Reach the client\n"
    for i, model in enumerate(order_models):
        print(i)
        orders += str(model['CreatedOn']).split('.')[0] + '; '
        orders += str(model['Order']['OrderInfo']['Number']) + '; '
        orders += str(model['Order']['DeliveryTimeSlot']['To']).split('.')[0] + '; '

        if 'CarrierInfo' in model['Order']:
            if model['Order']['CarrierInfo'] is not None:
                orders += carriers[str(model['Order']['CarrierInfo']['CarrierId'])]
        orders += '; '

        for state in model['StateHistory']:
            if state['State'] == 22:
                orders += str(state['Audit']['CreatedOn']).split('.')[0]
                break
        orders += '; '

        for event in model['OrderEvents']:
            if event['EventType'] == 4:
                orders += str(event['Audit']['CreatedOn']).split('.')[0]
                break
        orders += ';\n'

    f.write(orders)
    f.close()


if __name__ == '__main__':
    try:
        get_orders_by_company()
        atlas.stop_client()
    except Exception as e:
        print(e)
