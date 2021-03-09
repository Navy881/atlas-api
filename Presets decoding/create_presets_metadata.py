#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path


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


def create_presets_metadata():
    Path("./_metadata/").mkdir(parents=True, exist_ok=True)

    data = get_data(json_file_path=FEATURE_DESCRIPTIONS)

    for module in data['Modules']:
        Path("./_metadata/" + module['Name']).mkdir(parents=True, exist_ok=True)

        for feature in module['Features']:
            feature_name = feature['Name']
            feature_description = feature['Description']
            feature_presets = feature['Presets']
            Path("./_metadata/" + module['Name'] + "/Features/" + feature_name).mkdir(parents=True, exist_ok=True)

            with open("./_metadata/" + module['Name'] + "/Features/" + feature_name + "/IncludedSettings.json", 'w',
                      encoding='utf-8') as presets_file:
                json.dump(feature_presets, presets_file, indent=2)

            with open("./_metadata/" + module['Name'] + "/Features/" + feature_name + "/Description.md", 'w',
                      encoding='utf-8') as description_file:
                description_file.write(feature_description)


if __name__ == '__main__':
    try:
        create_presets_metadata()
    except Exception as e:
        print(e)
