import json
import time

from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)

if __name__ == '__main__':
    try:
        atlas.start_client()
        with open('legs.json', 'r', encoding="utf8") as f:
            data = json.load(f)

        legs = data
        i = 0
        atlas_legs = atlas.get_all_legs()
        for leg in legs:

            # if '-' in leg['start_point'] or '-' in leg['end_point']:
            #     print(leg['code'], leg['start_point'], '-', leg['end_point'])
            #
            # for other_leg in legs:
            #     if leg['code'] != other_leg['code'] and (leg['start_point'] in other_leg['start_point'] or
            #                                              other_leg['start_point'] in leg['start_point']) and \
            #             (leg['end_point'] in other_leg['end_point'] or other_leg['end_point'] in leg['end_point']):
            #         print(leg['code'], leg['start_point'], leg['end_point'], other_leg['code'],
            #               other_leg['start_point'], other_leg['end_point'])

            resp = atlas.create_leg(leg_external_id=leg['code'], stat_point_name=leg['start_point'],
                                    end_point_name=leg['end_point'].split('\n')[0])
            time.sleep(0.05)
            if resp is not None:
                i += 1
                print(i)
            else:
                print(leg)
                # end_point = leg['end_point'].split('\n')[0] + ' ' + leg['code']
                end_point = leg['end_point'].split('\n')[0]
                resp = atlas.create_leg(leg_external_id=leg['code'], stat_point_name=leg['start_point'],
                                        end_point_name=end_point)

            # for atlas_leg in atlas_legs:
            #     if 'ExternalId' in atlas_leg:
            #         if atlas_leg['ExternalId'] == leg['code']:
            #             atlas.remove_leg(atlas_leg['Id'])
            #
            #             time.sleep(0.05)
            #             i += 1
            #             print(i)
            #             # input('Press key')

    except Exception as e:
        print(e)
