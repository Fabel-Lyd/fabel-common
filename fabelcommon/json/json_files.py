def read_json_as_text(file):
    with open(file, 'r', encoding='utf-8') as json_file:
        return json_file.read()
