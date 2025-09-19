import json

DATA_FILE = 'assets/events.json'

def load_events():
    """Loads all volunteer events from the JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_events(events):
    """Saves the list of events back to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(events, f, indent=2)