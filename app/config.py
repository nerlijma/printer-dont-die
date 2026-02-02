import json
import os
import sys


def get_base_path():
    """
    Returns the base path for the application.
    If running from PyInstaller executable, returns the directory where the exe is located.
    Otherwise, returns the project root directory.
    """
    if getattr(sys, "frozen", False):
        # Running from PyInstaller executable
        return os.path.dirname(sys.executable)
    else:
        # Running from Python script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """
    Returns the absolute path to a resource file.
    Works both when running as script and as PyInstaller executable.
    """
    if getattr(sys, "frozen", False):
        # Running from PyInstaller executable
        # Resources are extracted to sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # Running from Python script
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


# --- Configuration Utilities ---
def load_config():
    """Loads configuration from config.json."""
    # First try to load from the executable directory (for PyInstaller)
    base_path = get_base_path()
    config_path = os.path.join(base_path, "config.json")

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Try current directory as fallback
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(
                f"Error: config.json not found. Looked in: {config_path} and current directory."
            )
            return None


def update_config(key, value):
    """Updates a single key in the configuration file."""
    config = load_config()
    if config:
        config[key] = value
        # Save to the same location where we loaded from
        base_path = get_base_path()
        config_path = os.path.join(base_path, "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)


def update_nested_config(keys, value):
    """
    Updates a nested key in the configuration file.
    keys: list of keys, e.g., ['refresh_token']
    """
    config = load_config()
    if not config:
        return False

    # Navigate to the nested dict
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Set the final value
    current[keys[-1]] = value

    # Save to the same location where we loaded from
    base_path = get_base_path()
    config_path = os.path.join(base_path, "config.json")
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save config: {e}")
        return False
