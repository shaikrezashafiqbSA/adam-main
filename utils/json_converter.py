import json

def json_dumps(row):
    return json.dumps(dict(row))

def json_loads(row):
    return json.loads(row)