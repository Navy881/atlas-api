import time
from datetime import datetime, timedelta

from AtlasApi import AtlasApiConnect

url = ''
username = ''
password = ''
atlas = AtlasApiConnect(url=url, username=username, password=password)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

orders = ['5d44e0c8-bccd-4243-aece-50cc0ae60893',
            '73e2b467-ba22-4dc4-984f-c9b1bfdd1d39',
            '3fab3e00-4a73-4041-a420-8bff0ce418d5',
            '02b4f149-3fcd-4f24-b9df-1a6558bb46d2',
            '1555df0a-b549-4166-a9a7-3fbb438dcd0b',
            'e2961839-5178-445f-aefa-8981a34f3a4a',
            '6686f7c2-fbb6-4c63-8864-909124ee1204',
            'c6947d2e-458f-4f36-9205-175958d5e0a9',
            'cb9f545d-fefa-43d7-83f8-8feb9b337556',
            '10ff316e-c7cb-4fe7-b159-81d4d4cce207',
            '8df07026-dee0-4416-b45b-32c68ba9c240',
            'b3ee58f5-c405-4f6e-8e4b-fa0b7a90c83f',
            '8cd7495a-71bc-4652-8b45-5336d977e78e',
            'f970add5-fffb-4198-9222-02a92049dfd3',
            'ca8d8050-09da-4932-90c5-7623521f12b2',
            '43c80083-a826-4a63-86fe-3434492d4398',
            'ed4416c7-62fb-417b-a00f-c7e7ce2b4e98',
            'e46aeb3a-9a83-4d33-ab98-9fb5df12c863',
            'fcb225c3-1543-42cc-b94b-488e9af0852b',
            '818da899-24f9-4649-9130-5f803fe3adb5',
            'dbf664e9-cf73-4ac3-bce6-ec2b207a69be',
            '227305fa-1291-45f8-adb8-45512882827e',
            '7195e882-f26c-463b-9b80-b78df2cd1407',
            'd2f33c31-ec88-4ae4-8041-1457f297a67d',
            'c82be65c-addf-4ad1-8d16-7eff43fe9c50',
            '9c990144-b496-4d07-a7de-239aec32750e',
            'b6a728dd-a49d-4978-8987-2ca17a257ef5',
            'f6473b86-b3af-416a-8433-d36df1096f79',
            '06518681-c2f8-4f65-a5e8-0a79296769d0',
            'db1fbc5f-a53c-4cf2-8f44-5525ad207944',
            '3ee951f1-84e1-44f3-a63f-4d44aa7206ff',
            'df5e300c-0a9f-462a-9c26-61aa85e1db7f',
            '2e591f3d-4431-4cc8-b7f3-7ba5e05530ef',
            'b69a403d-2a08-484d-a0c2-888c2e7f1749',
            '66c21923-2393-420c-b97d-f0a5be8415ac',
            'ab009a3e-9721-48e4-b792-66f41a202842',
            '875c5a47-cf7a-4c89-a536-136855ee746f'
          ]

routes = {
"6278acab-419f-40e1-b455-08093c0086b9": "Started",
"a1a0d19c-e3fb-4ec5-9242-14e27bb1e116": "Started",
"35df31f1-f30c-4a51-afb6-2aab9dd45871": "PerformerAccepted",
"6dabea72-e7b4-4578-8929-17ea75e94cf4": "PerformerAssigned",
"b3e1c9ca-d230-4bfb-b25e-632c47ada609": "PerformerAccepted",
"f2a2ca81-1206-4b25-a151-1e2691bfb644": "PerformerAccepted",
"e5294c36-aac9-47e5-a0cd-322e31933513": "SentToPerformer",
"17d62b48-7fdd-4cb4-8ac6-f811b1644811": "SentToPerformer",
"7177fd56-4221-4395-bff3-f30e1594e214": "Started",
"e968c8c1-74f8-4269-aa4b-f913d9b95624": "Started",
"e11a643a-5780-495e-80f8-b555077d8bf0": "SentToPerformer",
"2355cce9-de75-47f2-a4e6-2860f6c48de9": "SentToPerformer",
"9009a59e-b3cc-42c3-9f12-3d09c7a10993": "SentToPerformer",
"8f584292-9173-4b0d-8574-cc33697d18a4": "SentToPerformer",
"a1df864a-ac0c-4155-9c5b-125ada05bd1f": "SentToPerformer",
"b8d35a36-c1ef-4952-b96b-8347456f1790": "Started",
"384f59b2-20e1-4a91-ac13-715c9eaf7066": "SentToPerformer",
"294a0bd3-1b99-4189-8ee4-6f063f53e05c": "PerformerAccepted",
"a137ece8-9288-4768-a769-1786fea3af97": "Started",
"9fba17d9-ddc8-410d-ad56-32b002c210f3": "PerformerAccepted",
"bba8f639-dce6-4304-aa04-a2630a482ccf": "PerformerAccepted",
"6d51e4f3-da52-45fe-b23b-60f77ebe49f4": "Started",
"0dc8540f-aa23-4966-8f80-0e40a3be48ba": "Started",
"598125c3-6962-4fda-9ad7-1d2c97ad0653": "Started",
"ea726faa-58e1-476e-9125-5c43b95d2a88": "PerformerAccepted",
"9ddcfeed-3855-4d7c-b3b9-32c34f315032": "Started",
"515e7c5a-2a84-4606-b67d-80123555f09a": "Started",
"6d0c4894-78bc-4fc5-9f9f-589215a5a91a": "PerformerAccepted",
"bf1a9a22-488d-4b98-91f3-9aea2d3d7c0d": "Started",
"76ad0b64-c575-4c3c-84b9-7a153bf88643": "SentToPerformer",
"d8856d9b-d482-41f0-9af7-8a0dc6265639": "SentToPerformer"}

if __name__ == '__main__':
    try:
        atlas.start_client()
        load_point_states = []
        for i, order in enumerate(orders):
            # print(i)
            order_model = atlas.get_order_by_id(order_id=order)
            order_state_history = atlas.get_order_state_history(order_id=order)
            order_state = ''
            for o_state in order_state_history:
                if datetime.strptime(o_state['Audit']['CreatedOn'].split('Z')[0].split('.')[0], DATETIME_FORMAT) < datetime.strptime('2020-03-27T21:00:00', DATETIME_FORMAT):
                    order_state = o_state['State']
            # print('Order:', order, order_model['StateInfo']['State'], order_state)

            route = atlas.get_route_by_order_id(order_id=order)
            route_id = route[0]['Id']
            route_state_history = atlas.get_route_state_history(route_id=route_id)
            state_n = len(route_state_history)
            route_state = ''
            for state in route_state_history:
                if datetime.strptime(state['Audit']['CreatedOn'].split('Z')[0].split('.')[0], DATETIME_FORMAT) < datetime.strptime('2020-03-27T21:00:00', DATETIME_FORMAT):
                    route_state = state['State']
            print('Route:', route_id, route_state, route[0]['StateInfo']['State'])
            # print('"' + route_id + '": "' + route_state + '",')
            # load_point = route[0]['RoutePoints'][0]
            # load_point_id = load_point['Id']
            # load_point_history = atlas.get_route_point_history(route_point_id=load_point_id)
            # for event in load_point_history:
            #     if 'State' in event:
            #         load_point_states.append(event['State'])
            # point_stat_n = len(load_point_states)
            # print('LoadPoint:', load_point_id, load_point_states[point_stat_n-4], load_point_states[point_stat_n-1])
            # print('')
    except Exception as e:
        print(e)
