from AtlasApi import AtlasApiConnect

url = ''
username = ''
password = ''
atlas = AtlasApiConnect(url=stand, username=username, password=password)

LEG_EXTERNAL_ID = 'КлмнМск2'
DATE = '2019-12-02'

if __name__ == '__main__':
    try:
        atlas.start_client()
        orders = atlas.get_orders()
        i = 0
        if len(orders) > 0:
            for order in orders:
                if order['AddressInfo'] is not None:
                        # order['AddressInfo']['Country'] != '' and (order['AddressInfo']['Town'] != '' or
                        #                                       order['AddressInfo']['Region'] != '') \
                        # and order['AddressInfo']['Street'] != '' and order['AddressInfo']['Building'] != '':
                    print(order['Id'])
                    print(order['AddressInfo'])
                    print(order['AddressInfo']['District'], order['AddressInfo']['Town'],
                          order['AddressInfo']['Street'], order['AddressInfo']['Building'])
                    i += 1
            print(str(i) + '/' + str(len(orders)))
    except Exception as e:
        print(e)
