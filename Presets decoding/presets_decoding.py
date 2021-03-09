#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import webbrowser
import pandas as pd
from datetime import datetime

from AtlasApi import AtlasApiConnect

CLIENTS_ACCESS_SETTINGS = 'clients_access_settings.json'
FEATURE_DESCRIPTIONS = 'feature_descriptions.json'


def get_data(json_file_path: str):
    try:
        with open(json_file_path, encoding='utf-8') as f:
            data = json.loads(f.read())

        result = data
    except Exception as e:
        print('ERROR: file ' + json_file_path + ' reading:', e)
        result = None
    return result


def get_clients_presets():
    try:
        clients_presets = {}
        result = None

        with open(CLIENTS_ACCESS_SETTINGS, 'r') as f:
            clients_data = json.loads(f.read())

        if 'AtlasClients' in clients_data and type(clients_data['AtlasClients']) == list:
            for client_data in clients_data['AtlasClients']:

                print(f"\nINFO: {client_data['Name']}")
                atlas = AtlasApiConnect(url=client_data['Uri'],
                                        moloch_url=client_data['MolochUri'],
                                        username=client_data['Username'],
                                        password=client_data['Password'])
                atlas.start_client()

                response = atlas.get_preset()
                if response is not None:
                    clients_presets[client_data['Name']] = response
                    result = clients_presets

                atlas.stop_client()
                del atlas

                time.sleep(1)

        return result
    except Exception as e:
        print(e)
        return None


def check_contains(main_dict: dict, sub_dict: dict):
    result = True
    # main = pd.DataFrame.from_dict(main_dict, orient='index')
    # sub = pd.DataFrame.from_dict(sub_dict, orient='index')
    main = pd.DataFrame([main_dict]).T
    sub = pd.DataFrame([sub_dict]).T

    for index in sub.index:

        # Проверка наличия пресета в корне
        if index not in main.index:
            return False

        # Проверка наличия разрешения в матрице доступа
        # Собирает все роли для каждого разрешения
        # elif index == "PermissionMatrix" and "Any" in sub_dict[index]:
        #     permission_roles = "\nPermissions: "
        #     for permission in sub_dict[index]["Any"]:
        #         permission_in_matrix = False
        #         roles = ""
        #         for role in main_dict[index]:
        #             if permission in main_dict[index][role]:
        #                 permission_in_matrix = True
        #                 roles += role + '\n '
        #         if not permission_in_matrix:
        #             return False
        #         else:
        #             permission_roles += '\n' + permission + ' in roles:\n[' + roles + ']\n'
        #     result = permission_roles

        elif index == "PermissionMatrix" and "Any" in sub_dict[index]:
            for permission in sub_dict[index]["Any"]:
                permission_in_matrix = False
                for role in main_dict[index]:
                    if permission in main_dict[index][role]:
                        permission_in_matrix = True
                        break
                if not permission_in_matrix:
                    return False
            return result

        # Проверка объектов
        elif type(sub_dict[index]) is dict:
            res = check_contains(main_dict[index], sub_dict[index])
            if not res:
                return False
            else:
                result = res

        # Проверка наличия объекта в массиве
        elif type(sub_dict[index]) is list:
            for i in range(len(sub_dict[index])):
                if sub_dict[index][i] not in main_dict[index]:
                    return False
            result = True

        else:
            # Проверка соотвевтия значений пресетов
            if main_dict[index] == sub_dict[index]:
                result = True
            elif sub_dict[index] == "Any":
                result = main_dict[index]
            else:
                return False

    return result


def get_clients_features(clients_presets: dict):
    feature_descriptions = get_data(FEATURE_DESCRIPTIONS)

    for module in feature_descriptions['Modules']:
        clients_using_module = []
        print(f"\n\nModule: {module['Name']}")

        for feature in module['Features']:
            clients_using_feature = {}
            print(f"    Feature: {feature['Name']}")
            # print(f"{feature['Name']} {feature['Description']}")

            for client in clients_presets:
                client_preset = clients_presets[client]

                # if feature['Presets'].items() <= client_preset.items():
                feature_value = check_contains(main_dict=client_preset, sub_dict=feature['Presets'])
                if feature_value:
                    clients_using_feature[client] = feature_value
                    if client not in clients_using_module:
                        clients_using_module.append(client)
                    print(f"        {client} +")

            if "Clients" not in feature:
                feature["Clients"] = clients_using_feature

        if "Clients" not in module:
            module["Clients"] = clients_using_module

    return feature_descriptions


def create_report_for_company(clients_features: dict, company):
    report_name = f'{company} features.html'
    f = open(report_name, 'w')

    table = '<table class="fixtable">'

    table += '<thead>'
    table += '<tr>'
    table += '<th>№</th>'
    table += '<th>Модуль</th>'
    table += '<th>Возможность</th>'
    table += '<th>Описание</th>'
    table += '<th class="company_name">' + company + '</th>'
    table += '</tr>'
    table += '</thead>'

    table += '<tbody>'
    for i, module in enumerate(clients_features['Modules']):
        table += '<tbody class="labels">'
        table += '<tr class="module">' + \
                 '<td>' + str(i + 1) + '</td>' + \
                 '<td>' + \
                 '<input type="checkbox" data-toggle="toggle" class="css-checkbox" id="' + module['Name'] + '">' + \
                 '<label for="' + module['Name'] + '" class="css-label">' + \
                 '<span class="fa fa-chevron-up"></span>' + \
                 '<span class="fa fa-chevron-down"></span>' + \
                 ' ' + module['Name'] + '</td>' + \
                 '<td></td>' + \
                 '<td class="end_content"></td>'
        if company in module['Clients']:
            table += '<td class="status"><i class="fa fa-check"></i></td>'
        else:
            table += '<td class="status">-</td>'
        table += '</tr>'
        table += '</tbody>'

        table += '<tbody class="hide">'
        for j, feature in enumerate(module['Features']):
            table += '<tr>' + \
                     '<td>' + '&nbsp' * 3 + str(i + 1) + '.' + str(j + 1) + '</td>' + \
                     '<td></td>' + \
                     '<td>' + feature['Name'] + '</td>' + \
                     '<td class="end_content">' + feature['Description'] + '</td>'
            if company in feature['Clients']:
                if type(feature['Clients'][company]) is not bool and len(str(feature['Clients'][company])) < 400:
                    table += '<td class="status"><i class="fa fa-check"></i><br>' + \
                             str(feature['Clients'][company]) + '</td>'
                else:
                    table += '<td class="status"><i class="fa fa-check"></i></td>'
            else:
                table += '<td class="status">-</td>'

            table += '</tr>'
        table += '</tbody>'

    table += '</tbody>'
    table += '</table>'

    message = """
    <html>
    <head>
    <title>Companies features</title>
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1251">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="https://snipp.ru/cdn/jquery/2.1.1/jquery.min.js"></script>
    <script>
    function FixTable(table) {
        var inst = this;
        this.table  = table;

        $('tr > th',$(this.table)).each(function(index) {
            var div_fixed = $('<div/>').addClass('fixtable-fixed');
            var div_relat = $('<div/>').addClass('fixtable-relative');
            div_fixed.html($(this).html());
            div_relat.html($(this).html());
            $(this).html('').append(div_fixed).append(div_relat);
            $(div_fixed).hide();
        });

        this.StyleColumns();
        this.FixColumns();

        $(window).scroll(function(){
            inst.FixColumns()
        }).resize(function(){
            inst.StyleColumns()
        });
    }

    FixTable.prototype.StyleColumns = function() {
        var inst = this;
        $('tr > th', $(this.table)).each(function(){
            var div_relat = $('div.fixtable-relative', $(this));
            var th = $(div_relat).parent('th');
            $('div.fixtable-fixed', $(this)).css({
                'width': $(th).outerWidth(true) - parseInt($(th).css('border-left-width')) + 'px',
                'height': $(th).outerHeight(true) + 'px',
                'left': $(div_relat).offset().left - parseInt($(th).css('padding-left')) + 'px',
                'padding-top': $(div_relat).offset().top - $(inst.table).offset().top + 'px',
                'padding-left': $(th).css('padding-left'),
                'padding-right': $(th).css('padding-right')
            });
        });
    }

    FixTable.prototype.FixColumns = function() {
        var inst = this;
        var show = false;
        var s_top = $(window).scrollTop();
        var h_top = $(inst.table).offset().top;

        if (s_top < (h_top + $(inst.table).height() - $(inst.table).find('.fixtable-fixed').outerHeight()) && s_top > h_top) {
            show = true;
        }

        $('tr > th > div.fixtable-fixed', $(this.table)).each(function(){
            show ? $(this).show() : $(this).hide()
        });
    }

    $(document).ready(function(){
        $('.fixtable').each(function() {
            new FixTable(this);
        });
    });
    </script>

    <script type="text/javascript">  
        $(document).ready(function() {
            $('[data-toggle="toggle"]').change(function(){
                $(this).parents().next('.hide').toggle();
            });
        }); 
    </script>  

    <style>
    h1, h2, h3, p {
        font-family: Calibri;
    }
    table {
        border-spacing: 0;
        width: 100%;
        border: 1px solid #ddd;
        font-family: Calibri;
    }

    .fixtable-fixed {
        position: fixed;
        top: 0;
        z-index: 101;
        background-color: #343B4C;
        border-bottom: 1px solid #ddd;
    }

    th, td {
        text-align: left;
        padding: 16px;
    }

    th {
        background-color: #343B4C;
        color: #fff;
        position: sticky;
    }

    tr:nth-child(even) td.status{
        background-color: #F3F3F3
    }

    tr.module { 
        background: #549ee3; 
        color: white;
        height: 40px;
        border-bottom: 1px solid maroon;
    }

    tr.module td { 
        border-bottom: 1px solid maroon;
    }

    th.company_name, td.status { 
        text-align: center;
    }

    td.end_content {
        border-right: 1px solid maroon;
    }

    .fa-check {
        color: green;
    }

    .fa-remove {
        color: red;
    }

    tbody tr:hover:not(.module) {
        background: #cfd2d4; /* Цвет фона при наведении */
        color: #fff; /* Цвет текста при наведении */
    }

    .css-label {
      cursor: pointer;
    }

    .css-checkbox {
      display: none;
    }

    .fa-chevron-up {
      display: none;
    }

    .css-checkbox:checked + .css-label .fa-chevron-up {
      display: inline;
    }

    .css-checkbox:checked + .css-label .fa-chevron-down {
      display: none;
    }

    img {
        max-height: 260px;
        max-width: 260px;
        padding: 2px;
        width: 100%;
        display: block;
        float:left;
        margin: 7px 7px 30px 0;
    }
    </style>

    <!-- add icon link -->
    <link rel="shortcut icon" type="image/x-icon" href="favicon.ico"/>

    </head>
    <body>
    <h3>Настройки возможностей системы по клиентам</h3>
    <p>Описание всех возможностей системы см. 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/744980510/Presets">тут</a> и 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/419397844">тут.</a></p>
    """ + table + """ 
    </body>
    </html>
    """

    f.write(message)
    f.close()


def create_report(clients_presets: dict, clients_features: dict):
    report_name = 'Companies features.html'
    f = open(report_name, 'w')

    table = '<table id="table">'

    table += '<thead>'
    table += '<tr>'
    table += '<th>№</th>'
    table += '<th>Модуль</th>'
    table += '<th>Возможность</th>'
    table += '<th>Описание</th>'
    for company in clients_presets:
        table += '<th class="company_name">' + company + '</th>'
    table += '</tr>'
    table += '</thead>'

    table += '<tbody>'
    for i, module in enumerate(clients_features['Modules']):
        table += '<tbody class="labels">'
        table += '<tr class="module">' + \
                 '<td>' + str(i + 1) + '</td>' + \
                 '<td>' + \
                 '<input type="checkbox" data-toggle="toggle" class="css-checkbox" id="' + module['Name'] + '">' + \
                 '<label for="' + module['Name'] + '" class="css-label">' + \
                 '<span class="fa fa-chevron-up"></span>' + \
                 '<span class="fa fa-chevron-down"></span>' + \
                 ' ' + module['Name'] + '</td>' + \
                 '<td></td>' + \
                 '<td class="end_content"></td>'
        for company in clients_presets:
            if company in module['Clients']:
                table += '<td class="status"><i class="fa fa-check"></i></td>'
            else:
                table += '<td class="status">-</td>'
        table += '</tr>'
        table += '</tbody>'

        table += '<tbody class="hide">'
        for j, feature in enumerate(module['Features']):

            if feature['Name'] == 'ProductRestrictions':
                print(1)

            table += '<tr>' + \
                     '<td>' + '&nbsp' * 3 + str(i + 1) + '.' + str(j + 1) + '</td>' + \
                     '<td></td>' + \
                     '<td>' + feature['Name'] + '</td>' + \
                     '<td class="end_content">' + feature['Description'] + '</td>'
            for company in clients_presets:
                if company in feature['Clients']:
                    if type(feature['Clients'][company]) is not bool and len(str(feature['Clients'][company])) < 400:
                        table += '<td class="status"><i class="fa fa-check"></i><br>' + \
                                 str(feature['Clients'][company]) + '</td>'
                    else:
                        table += '<td class="status"><i class="fa fa-check"></i></td>'
                else:
                    table += '<td class="status">-</td>'

            table += '</tr>'
        table += '</tbody>'

    table += '</tbody>'
    table += '</table>'

    message = """
    <html>
    <head>
    <title>Companies features</title>
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1251">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="https://snipp.ru/cdn/jquery/2.1.1/jquery.min.js"></script>
    
    <script type="text/javascript">  
        $(document).ready(function() {
            $('[data-toggle="toggle"]').change(function(){
                $(this).parents().next('.hide').toggle();
            });
        }); 
    </script>  

    <style>
    h1, h2, h3, p {
        font-family: Calibri;
    }
    
    table {
        border-spacing: 0;
        width: 100%;
        border: 1px solid #ddd;
        font-family: Calibri;
    }

    th, td {
        text-align: left;
        padding: 16px;
    }

    th {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 2;
        background-color: #343B4C;
        color: #fff;
    }

    tr:nth-child(even) td.status{
        background-color: #F3F3F3
    }
    
    tr.module { 
        background: #549ee3; 
        color: white;
        height: 40px;
        border-bottom: 1px solid maroon;
    }

    tr.module td { 
        border-bottom: 1px solid maroon;
    }

    th.company_name, td.status { 
        text-align: center;
    }

    td.end_content {
        border-right: 1px solid maroon;
    }

    .fa-check {
        color: green;
    }

    .fa-remove {
        color: red;
    }

    tbody tr:hover:not(.module) {
        background: #cfd2d4; /* Цвет фона при наведении */
        color: #ff0000; /* Цвет текста при наведении */
    }

    .css-label {
      cursor: pointer;
    }

    .css-checkbox {
      display: none;
    }

    .fa-chevron-up {
      display: none;
    }

    .css-checkbox:checked + .css-label .fa-chevron-up {
      display: inline;
    }

    .css-checkbox:checked + .css-label .fa-chevron-down {
      display: none;
    }
    
    img {
        max-height: 260px;
        max-width: 260px;
        padding: 2px;
        width: 100%;
        display: block;
        float:left;
        margin: 7px 7px 30px 0;
    }

    </style>
    
    <!-- add icon link -->
    <link rel="shortcut icon" type="image/x-icon" href="favicon.ico"/>
    
    </head>
    <body>
    <h3>Настройки возможностей системы по клиентам от """ + datetime.now().strftime("%d.%m.%Y") + """</h3>
    <p>Описание всех возможностей системы см. 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/744980510/Presets">тут</a> и 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/419397844">тут.</a></p>
    """ + table + """ 
    </body>
    </html>
    """

    f.write(message)
    f.close()
    webbrowser.open_new_tab(report_name)


'''
Fix JS
def create_report(clients_presets: dict, clients_features: dict):
    report_name = 'Companies features.html'
    f = open(report_name, 'w')

    table = '<table class="fixtable">'

    table += '<thead>'
    table += '<tr>'
    table += '<th>№</th>'
    table += '<th>Модуль</th>'
    table += '<th>Возможность</th>'
    table += '<th>Описание</th>'
    for company in clients_presets:
        table += '<th class="company_name">' + company + '</th>'
    table += '</tr>'
    table += '</thead>'

    table += '<tbody>'
    for i, module in enumerate(clients_features['Modules']):
        table += '<tbody class="labels">'
        table += '<tr class="module">' + \
                 '<td>' + str(i + 1) + '</td>' + \
                 '<td>' + \
                 '<input type="checkbox" data-toggle="toggle" class="css-checkbox" id="' + module['Name'] + '">' + \
                 '<label for="' + module['Name'] + '" class="css-label">' + \
                 '<span class="fa fa-chevron-up"></span>' + \
                 '<span class="fa fa-chevron-down"></span>' + \
                 ' ' + module['Name'] + '</td>' + \
                 '<td></td>' + \
                 '<td class="end_content"></td>'
        for company in clients_presets:
            if company in module['Clients']:
                table += '<td class="status"><i class="fa fa-check"></i></td>'
            else:
                table += '<td class="status">-</td>'
        table += '</tr>'
        table += '</tbody>'

        table += '<tbody class="hide">'
        for j, feature in enumerate(module['Features']):
            table += '<tr>' + \
                     '<td>' + '&nbsp' * 3 + str(i + 1) + '.' + str(j + 1) + '</td>' + \
                     '<td></td>' + \
                     '<td>' + feature['Name'] + '</td>' + \
                     '<td class="end_content">' + feature['Description'] + '</td>'
            for company in clients_presets:
                if company in feature['Clients']:
                    if type(feature['Clients'][company]) is not bool and len(str(feature['Clients'][company])) < 400:
                        table += '<td class="status"><i class="fa fa-check"></i><br>' + \
                                 str(feature['Clients'][company]) + '</td>'
                    else:
                        table += '<td class="status"><i class="fa fa-check"></i></td>'
                else:
                    table += '<td class="status">-</td>'

            table += '</tr>'
        table += '</tbody>'

    table += '</tbody>'
    table += '</table>'

    message = """
    <html>
    <head>
    <title>Companies features</title>
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1251">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="https://snipp.ru/cdn/jquery/2.1.1/jquery.min.js"></script>
    
    <script>
    function FixTable(table) {
        var inst = this;
        this.table  = table;

        $('tr > th',$(this.table)).each(function(index) {
            var div_fixed = $('<div/>').addClass('fixtable-fixed');
            var div_relat = $('<div/>').addClass('fixtable-relative');
            div_fixed.html($(this).html());
            div_relat.html($(this).html());
            $(this).html('').append(div_fixed).append(div_relat);
            $(div_fixed).hide();
        });

        this.StyleColumns();
        this.FixColumns();

        $(window).scroll(function(){
            inst.FixColumns()
        }).resize(function(){
            inst.StyleColumns()
        });
    }

    FixTable.prototype.StyleColumns = function() {
        var inst = this;
        $('tr > th', $(this.table)).each(function(){
            var div_relat = $('div.fixtable-relative', $(this));
            var th = $(div_relat).parent('th');
            $('div.fixtable-fixed', $(this)).css({
                'width': $(th).outerWidth(true) - parseInt($(th).css('border-left-width')) + 'px',
                'height': $(th).outerHeight(true) + 'px',
                'left': $(div_relat).offset().left - parseInt($(th).css('padding-left')) + 'px',
                'padding-top': $(div_relat).offset().top - $(inst.table).offset().top + 'px',
                'padding-left': $(th).css('padding-left'),
                'padding-right': $(th).css('padding-right')
            });
        });
    }

    FixTable.prototype.FixColumns = function() {
        var inst = this;
        var show = false;
        var s_top = $(window).scrollTop();
        var h_top = $(inst.table).offset().top;

        if (s_top < (h_top + $(inst.table).height() - $(inst.table).find('.fixtable-fixed').outerHeight()) && s_top > h_top) {
            show = true;
        }

        $('tr > th > div.fixtable-fixed', $(this.table)).each(function(){
            show ? $(this).show() : $(this).hide()
        });
    }

    $(document).ready(function(){
        $('.fixtable').each(function() {
            new FixTable(this);
        });
    });
    </script>

    <script type="text/javascript">  
        $(document).ready(function() {
            $('[data-toggle="toggle"]').change(function(){
                $(this).parents().next('.hide').toggle();
            });
        }); 
    </script>  

    <style>
    h1, h2, h3, p {
        font-family: Calibri;
    }
    
    table {
        border-spacing: 0;
        width: 100%;
        border: 1px solid #ddd;
        font-family: Calibri;
    }

    .fixtable-fixed {
        position: fixed;
        top: 0;
        z-index: 101;
        background-color: #343B4C;
        border-bottom: 1px solid #ddd;
    }

    th, td {
        text-align: left;
        padding: 16px;
    }

    th {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 2;
        background-color: #343B4C;
        color: #fff;
    }

    tr:nth-child(even) td.status{
        background-color: #F3F3F3
    }
    
    tr.module { 
        background: #549ee3; 
        color: white;
        height: 40px;
        border-bottom: 1px solid maroon;
    }

    tr.module td { 
        border-bottom: 1px solid maroon;
    }

    th.company_name, td.status { 
        text-align: center;
    }

    td.end_content {
        border-right: 1px solid maroon;
    }

    .fa-check {
        color: green;
    }

    .fa-remove {
        color: red;
    }

    tbody tr:hover:not(.module) {
        background: #cfd2d4; /* Цвет фона при наведении */
        color: #ff0000; /* Цвет текста при наведении */
    }

    .css-label {
      cursor: pointer;
    }

    .css-checkbox {
      display: none;
    }

    .fa-chevron-up {
      display: none;
    }

    .css-checkbox:checked + .css-label .fa-chevron-up {
      display: inline;
    }

    .css-checkbox:checked + .css-label .fa-chevron-down {
      display: none;
    }
    
    img {
        max-height: 260px;
        max-width: 260px;
        padding: 2px;
        width: 100%;
        display: block;
        float:left;
        margin: 7px 7px 30px 0;
    }
    </style>
    
    <!-- add icon link -->
    <link rel="shortcut icon" type="image/x-icon" href="favicon.ico"/>
    
    </head>
    <body>
    <img src="atlas_logo.png", alt="logo", class="logo">
    <h3>Настройки возможностей системы по клиентам от """ + datetime.now().strftime("%d.%m.%Y") + """</h3>
    <p>Описание всех возможностей системы см. 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/744980510/Presets">тут</a> и 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/419397844">тут.</a></p>
    """ + table + """ 
    </body>
    </html>
    """

    f.write(message)
    f.close()
    webbrowser.open_new_tab(report_name)
'''


'''
def create_report(clients_presets: dict, clients_features: dict):
    report_name = 'Companies features.html'
    f = open(report_name, 'w')

    table = '<table id="table", class="fixtable">'

    table += '<thead>'
    table += '<tr>'
    table += '<th class="hard_left">№</th>'
    table += '<th>Модуль</th>'
    table += '<th>Возможность</th>'
    table += '<th>Описание</th>'
    for company in clients_presets:
        table += '<th class="company_name">' + company + '</th>'
    table += '</tr>'
    table += '</thead>'

    table += '<tbody>'
    for i, module in enumerate(clients_features['Modules']):
        table += '<tbody class="labels">'
        table += '<tr class="module">' + \
                 '<td>' + str(i + 1) + '</td>' + \
                 '<td>' + \
                 '<input type="checkbox" data-toggle="toggle" class="css-checkbox" id="' + module['Name'] + '">' + \
                 '<label for="' + module['Name'] + '" class="css-label">' + \
                 '<span class="fa fa-chevron-up"></span>' + \
                 '<span class="fa fa-chevron-down"></span>' + \
                 ' ' + module['Name'] + '</td>' + \
                 '<td></td>' + \
                 '<td class="end_content"></td>'
        for company in clients_presets:
            if company in module['Clients']:
                table += '<td class="status"><i class="fa fa-check"></i></td>'
            else:
                table += '<td class="status">-</td>'
        table += '</tr>'
        table += '</tbody>'

        table += '<tbody class="hide">'
        for j, feature in enumerate(module['Features']):
            table += '<tr>' + \
                     '<td>' + '&nbsp' * 3 + str(i + 1) + '.' + str(j + 1) + '</td>' + \
                     '<td></td>' + \
                     '<td>' + feature['Name'] + '</td>' + \
                     '<td class="end_content">' + feature['Description'] + '</td>'
            for company in clients_presets:
                if company in feature['Clients']:
                    if type(feature['Clients'][company]) is not bool and len(str(feature['Clients'][company])) < 400:
                        table += '<td class="status"><i class="fa fa-check"></i><br>' + \
                                 str(feature['Clients'][company]) + '</td>'
                    else:
                        table += '<td class="status"><i class="fa fa-check"></i></td>'
                else:
                    table += '<td class="status">-</td>'

            table += '</tr>'
        table += '</tbody>'

    table += '</tbody>'
    table += '</table>'

    message = """
    <html>
    <head>
    <title>Companies features</title>
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1251">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    
    <style>
    h1, h2, h3, p {
        font-family: Calibri;
    }

    .fa-check {
        color: green;
    }

    .fa-remove {
        color: red;
    }

    .css-label {
      cursor: pointer;
    }

    .css-checkbox {
      display: none;
    }

    .fa-chevron-up {
      display: none;
    }

    .css-checkbox:checked + .css-label .fa-chevron-up {
      display: inline;
    }

    .css-checkbox:checked + .css-label .fa-chevron-down {
      display: none;
    }

    img {
        max-height: 260px;
        max-width: 260px;
        padding: 2px;
        width: 100%;
        display: block;
        float:left;
        margin: 7px 7px 30px 0;
    }
    
    table {
      table-layout: fixed; 
      width: 100%;
      *margin-left: -100px;
    }
    td, th {
      vertical-align: top;
      border-top: 1px solid #ccc;
      padding:10px;
      width:100px;
    }
    th {
      width:100px;
    }
    .hard_left {
      position:absolute;
      left:0; 
      width:100px;
    }
    .next_left {
      position:absolute;
      left:100px; 
      width:100px;
    }
    
    th {
      position: -webkit-sticky;
      position: sticky;
      top: 0;
      z-index: 2;
    }
    
    </style>

    <!-- add icon link -->
    <link rel="shortcut icon" type="image/x-icon" href="favicon.ico"/>

    </head>
    <body>
    <img src="atlas_logo.png", alt="logo", class="logo">
    <h3>Настройки возможностей системы по клиентам от """ + datetime.now().strftime("%d.%m.%Y") + """</h3>
    <p>Описание всех возможностей системы см. 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/744980510/Presets">тут</a> и 
    <a href="https://atlasdelivery.atlassian.net/wiki/spaces/LM/pages/419397844">тут.</a></p>
    """ + table + """ 
    </body>
    </html>
    """

    f.write(message)
    f.close()
    webbrowser.open_new_tab(report_name)
'''


if __name__ == '__main__':
    try:
        clients_presets = get_clients_presets()

        clients_features = get_clients_features(clients_presets)

        # for company in clients_presets:
        #     create_report_for_company(clients_features, company)

        create_report(clients_presets, clients_features)
    except Exception as e:
        print(e)
