import json


# --- Configuration Utilities ---
def load_config():
    """Loads configuration from config.json."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create it with printer info.")
        return None


def update_config(key, value):
    """Updates a single key in the configuration file."""
    config = load_config()
    if config:
        config[key] = value
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
