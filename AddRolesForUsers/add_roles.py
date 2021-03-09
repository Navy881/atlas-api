
from AtlasApi import AtlasApiConnect

stand = ''
username = ''
password = ''
moloch = ''

atlas = AtlasApiConnect(url=stand, moloch_url=moloch, username=username, password=password)

if __name__ == '__main__':
    try:
        atlas.start_client()
        users = atlas.get_users_from_moloch()
        print(len(users), 'users')
        for user in users:
            company = atlas.get_company(user['CompanyId'])

            if company['Name'] == 'Beluga' and 'Administrator' in user['Roles']:
                print(company['Name'], user['Username'], user['Roles'])
                atlas.add_role_for_user(user_id=user['Id'], role='ForwarderManager')

            if 'Carrier' in company['Types'] and company['Name'] != 'Beluga' and 'HubManager' in user['Roles']:
                print(company['Name'], user['Username'], user['Roles'])
                atlas.add_role_for_user(user_id=user['Id'], role='CarrierManager')

    except Exception as e:
        print(e)