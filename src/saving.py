import json
file_path = "counter.json"

def load():
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save(data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
        
def reset():
    save({})
