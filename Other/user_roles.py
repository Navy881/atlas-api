
from AtlasApi import AtlasApiConnect

url = ''
username = ''
password = ''
moloch_url = ''
atlas = AtlasApiConnect(url=url, moloch_url=moloch_url, username=username, password=password)

not_interest_roles = ["CarrierManager", "RoutesBiddingCompetitor"]
Cedrus_id = 'f4421f9e-5962-4c68-8049-a45600f36f4b'

if __name__ == '__main__':
    try:
        atlas.start_client()
        users = atlas.get_users_from_moloch()
        for user in users:
            if user['CompanyId'] != Cedrus_id:
                for role in user['Roles']:
                    if role not in not_interest_roles:
                        print(role)
    except Exception as e:
        print(e)
