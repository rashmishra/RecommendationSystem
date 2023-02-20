import json

def parse_json(input_str):
    try:
        return json.loads(input_str)
    except json.JSONDecodeError as e:
        print(f"Malformed json ({e})")

def get_double_list(j):
    return [float(val) for val in j]
