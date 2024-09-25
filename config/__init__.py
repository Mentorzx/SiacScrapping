import os
import sys

import yaml

from .settings_loader import load_settings

config = load_settings()


def save_data(data) -> bool:
    """
    Save login data to the config.yaml file.

    Parameters:
    data (dict): The login data to be saved.
    """
    config.update(data)
    config_path = get_config_path()
    return write_to_yaml(config_path, config)


def get_config_path() -> str:
    """
    Get the path to the config.yaml file.

    Returns:
    str: The absolute path to the config.yaml file.
    """
    if getattr(sys, "frozen", False):
        project_root = os.path.abspath(os.path.dirname(sys.executable))
    else:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_directory = os.path.join(project_root, "config")
    return os.path.join(config_directory, "config.yaml")


def write_to_yaml(file_path, data) -> bool:
    """
    Write data to a YAML file in an organized and readable format.

    Parameters:
    file_path (str): The path to the YAML file.
    data (dict): The data to be written to the file.

    Returns:
    bool: The success.
    """
    try:
        with open(file_path, "w") as config_file:
            yaml.dump(
                data,
                config_file,
                default_flow_style=False,
                sort_keys=False,
                indent=4,
                width=80,
            )
        return True
    except Exception as e:
        print(f"Failed to write config: {e}")
        return False
