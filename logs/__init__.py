import os

from config import config

from .log import Logger

if os.path.exists(os.path.abspath(config["log"]["dir"])):
    for file in os.listdir(os.path.abspath(config["log"]["dir"])):
        if file.endswith(config["log"]["log_file_extension"]):
            os.remove(os.path.join(os.path.abspath(config["log"]["dir"]), file))

general_log = Logger()
return_log = Logger("return")
