
import datetime
import uuid
from pymongo import MongoClient
from bson.binary import CSHARP_LEGACY, UUID_SUBTYPE, PYTHON_LEGACY
from bson.codec_options import CodecOptions

from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''
moloch = ''

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

atlas = AtlasApiConnect(url=stand, username=username, password=password)


def get_tnt():
    filename = 'tnt' + str(datetime.datetime.now()).split(' ')[0] + '.csv'
    f = open(filename, "a")

    atlas.start_client()

    order_collection = db.get_collection('Order', CodecOptions(uuid_representation=CSHARP_LEGACY))
    tnt_collection = db.get_collection('TrackAndTrace', CodecOptions(uuid_representation=CSHARP_LEGACY))
    tnt_models = tnt_collection.find({"TrackAndTraceModel.Confirmation.ConfirmationInfo.Rating": {'$ne': None}})
    print(tnt_models.count())

    report = "Дата создания; Номер заказа; Грузополучатель; Рейтинг; Комментарий\n"

    for i, model in enumerate(tnt_models):
        print(i)
        order_id = model['TrackAndTraceModel']['OrderInfo']['OrderId']
        order = order_collection.find({"_id": uuid.UUID(str(order_id))})[0]

        report += str(model['CreatedOn']).split('.')[0] + '; '

        report += model['TrackAndTraceModel']['OrderInfo']['OrderNumber'] + '; '

        if order['Order']['ConsigneeInfo']['Company'] is not None:
            report += order['Order']['ConsigneeInfo']['Company']
        report += '; '

        report += str(model['TrackAndTraceModel']['Confirmation']['ConfirmationInfo']['Rating']) + '; '

        if model['TrackAndTraceModel']['Confirmation']['ConfirmationInfo']['Comments'] is not None:
            comments = model['TrackAndTraceModel']['Confirmation']['ConfirmationInfo']['Comments']
            for comment in comments:
                report += comment['Comment']
        report += ';\n'

    f.write(report)
    f.close()


if __name__ == '__main__':
    try:
        get_tnt()
        atlas.stop_client()
    except Exception as e:
        print(e)
