import os
import yaml


def load_settings(
    config_file: str = os.path.join(os.path.dirname(__file__), "config.yaml")
) -> dict:
    """
    Load YAML configuration from the given file.

    :param config_file: Path to the YAML configuration file
    :return: Dictionary containing the loaded settings
    """
    with open(config_file, "r") as file:
        return yaml.safe_load(file)
