import json

def load_settings():
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
            for key, value in settings.items():
                globals()[key] = value
    except FileNotFoundError:
        print("settings.json file not found.")
    except json.JSONDecodeError:
        print("Error decoding settings.json file.")

# Load settings on module import
load_settings()