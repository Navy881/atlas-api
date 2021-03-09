import json

# symbolList = []

#
# f = open("1.txt", "r+", )
# r = f.read()

legs = []

for line in open('legs.txt', 'r', encoding="utf8"):
    leg_info = {}
    print(line)
    leg = line.split('	')
    leg_info['code'] = leg[0]
    print(leg[0])

    points = leg[1].split('-', 1)
    if len(points) < 2:
        points = leg[1].split('–', 1)
    print(points[0].strip(' '))

    end_point = ''
    if len(points) > 1:
        print(points[1].strip(' '))
        leg_info['start_point'] = points[0].strip(' ')
        leg_info['end_point'] = points[1].strip(' ')
    else:
        leg_info['start_point'] = leg[0].strip(' ')
        leg_info['end_point'] = points[0].strip(' ')
    print('**************************')
    legs.append(leg_info)

# print(legs)

with open('legs.json', 'w', encoding="utf8") as f:
    json.dump(legs, f)

# with open('legs.json', 'r', encoding="utf8") as f:
#     data = json.load(f)

# datas = json.dumps(data, sort_keys=False,  indent=4, ensure_ascii=False,  separators=(',', ': '))

