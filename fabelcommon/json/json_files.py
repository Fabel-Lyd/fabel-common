import json


def read_json_as_text(file):
    with open(file, 'r', encoding='utf-8') as json_file:
        return json_file.read()


def read_json_data(file):
    with open(file, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        return json_data
