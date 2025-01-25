import re
import yaml
from pathlib import Path

def sanitize_filename(name):
    """Sanitize the channel name to be file-folder friendly."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def save_config(path, config):
    with open(path, "w") as f:
        yaml.safe_dump(config, f)