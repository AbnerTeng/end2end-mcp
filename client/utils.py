from typing import Any, Dict

import json


def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"Loaded configuration from {config_path}")

        return config

    except FileNotFoundError:
        print(f"Config file {config_path} not found")

        return {}

    except json.JSONDecodeError:
        print(f"Error parsing config file: {config_path}")

        return {}
