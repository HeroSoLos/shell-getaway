import json

"""
Deserializes a JSON string into Python data.
Args:
    string_data (str): The JSON string received over the network.
Returns:
    dict: The deserialized Python dictionary or list.
            Returns None or raises an exception if deserialization fails.
"""
def read_pos(string_data):
    try:
        return json.loads(string_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

"""
Serializes Python data (dict or list) into a JSON string for network transmission.
Args:
    data (dict/list): The Python data to serialize.
Returns:
    str: The JSON string representation of the data.
"""
def make_pos(data):
    return json.dumps(data)