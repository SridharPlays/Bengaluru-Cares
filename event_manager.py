import json

DATA_FILE = 'assets/events.json'

def load_events():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_events(events):
    with open(DATA_FILE, 'w') as f:
        json.dump(events, f, indent=2)