import json, time

def save_json(obj, filename='optional', path='./data'):
    if filename == 'optional':
        filename = time.time()
    with open(f'{path}/{filename}.json', 'w') as f:
        json.dump(obj, f)

def sqlite_escape(string):
    string = string.replace('"', '""')
    string = string.replace("\'", "''")
    return string
