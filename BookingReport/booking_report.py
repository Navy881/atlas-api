
import datetime
from AtlasApi import AtlasApiConnect
from pymongo import MongoClient

stand = ''
username = ''
password = ''
atlas = AtlasApiConnect(url=stand, username=username, password=password)

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


if __name__ == '__main__':
    try:
        start = datetime.datetime(2019, 11, 1)
        end = datetime.datetime(2019, 12, 1)

        atlas.start_client()

        collection = db['Route']
        routes = collection.find({"Route.CarrierInfo.Audit.CreatedOn": {'$gte': start, '$lt': end},
                                  "Route.RoutePoints.RoutePointInfo.PointType": 0})
        print('Route count:', routes.count())

        for route in routes:
            route_points = route['Route']['RoutePoints']
            for route_point in route_points:
                if route_point['RoutePointInfo']['PointType'] == 0:
                    print(route_point)

    except Exception as e:
        print(e)
