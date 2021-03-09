
import json
import psycopg2
from deepmerge import always_merger, conservative_merger, Merger

conn_cloud = psycopg2.connect(dbname='', user='',
                              password='', host='')

conn_ced = psycopg2.connect(dbname='', user='',
                            password='', host='')

conn_chain = psycopg2.connect(dbname='', user='',
                              password='', host='')

conn_trvl = psycopg2.connect(dbname='', user='',
                             password='', host='')

my_merger = Merger(
    [
        (list, "append"),
        (dict, "merge")
    ],
    ["override"],
    ["use_existing"]
)


def get_company_settings():
    try:
        cursor_cloud = conn_cloud.cursor()
        cursor_ced = conn_ced.cursor()
        cursor_chain = conn_chain.cursor()
        cursor_trvl = conn_trvl.cursor()

        cursor_cloud.execute('SELECT "Settings" FROM dbo."Companies"')
        cursor_ced.execute('SELECT "Settings" FROM dbo."Companies"')
        cursor_chain.execute('SELECT "Settings" FROM dbo."Companies"')
        cursor_trvl.execute('SELECT "Settings" FROM dbo."Companies"')

        print('Data received')

        res = json.loads('{}')

        for cursor in [cursor_cloud, cursor_ced, cursor_chain, cursor_trvl]:
            for row in cursor:
                if row[0] is not None:
                    settings = json.loads(row[0])
                    for key in settings.keys():
                        if key not in res:
                            res[key] = settings[key]

        print(res)

        cursor_cloud.close()
        cursor_ced.close()
        cursor_chain.close()
        cursor_trvl.close()
        conn_cloud.close()
        conn_ced.close()
        conn_chain.close()
        conn_trvl.close()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        get_company_settings()

    except Exception as e:
        print(e)
