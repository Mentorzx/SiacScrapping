import os
import sys

import yaml


def load_settings(config_file: str = None) -> dict:
    """
    Load YAML configuration from the given file.

    :param config_file: Path to the YAML configuration file
    :return: Dictionary containing the loaded settings
    """
    if config_file is None:
        if getattr(sys, "frozen", False):
            config_file = os.path.join(
                os.path.dirname(sys.executable), "config/config.yaml"
            )
        else:
            config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_file, "r") as file:
        return yaml.safe_load(file)
