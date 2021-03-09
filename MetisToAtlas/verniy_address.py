# !/usr/bin/env python3

import csv
import re

verniy_input_txt = "rep_2_3.txt"
# индекс колонки с ID заказа:
ID_COLUMN = 0
# индекс колонки с адресом:
ADDRESS_COLUMN = 4
verniy_input_csv = "verny1-orders-with-address.csv"
verniy_ouput = "Маршруты_Решение_3_с_адресами.txt"
regex = r"\s+Заказы:\s([0-9]{8})"

with open(verniy_input_csv, 'r', encoding="utf8") as vc:
    with open(verniy_input_txt, 'r', encoding="utf8") as vt:
        with open(verniy_ouput, 'w', encoding="utf8") as vo:
            reader = csv.reader(vc)

            result = ""
            address_map = {}
            index = 0
            for line in reader:
                if index > 2 and len(line) > 3:
                    address_map[line[ID_COLUMN]] = line[ADDRESS_COLUMN]

                index += 1

            content = vt.readlines()
            is_delivery = False
            for line in content:
                address = None

                if "Выгрузка" in line:
                    is_delivery = True

                matches = re.finditer(regex, line, re.MULTILINE)

                for matchNum, match in enumerate(matches, start=1):

                    for groupNum in range(0, len(match.groups())):
                        groupNum = groupNum + 1

                        address = match.group(groupNum)

                if not "Заказы2" in line:
                    result += line
                if address is not None and is_delivery:
                    result += f"   Адрес: {address_map[address]}\n"
                    is_delivery = False

            vo.write(result)
