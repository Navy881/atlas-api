from AtlasApi import AtlasApiConnect

url = ''
username = ''
password = ''

atlas = AtlasApiConnect(url=url, username=username, password=password)

if __name__ == '__main__':
    try:
        atlas.start_client()
        persons = atlas.get_all_persons()

        i = 0
        for person in persons:
            person_schedules = atlas.get_schedule_by_person_id(person_id=person['Id'])
            if len(person_schedules) > 0:
                i += 1

        print(f'Всего водителей: {len(persons)}\nВсего расписаний водителей: {i}')

    except Exception as e:
        print(e)
