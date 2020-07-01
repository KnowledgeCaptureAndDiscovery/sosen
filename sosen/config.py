from pathlib import Path
import os
import yaml

_config = None

config_file = "~/.sosen/config.yml"

def configure(sparql_endpoint):
    _config = {"endpoint": sparql_endpoint}

    print(_config)
    config_path = os.path.expanduser(config_file)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as out_file:
        print(yaml.dump(_config))
        out_file.write(yaml.dump(_config))

def get_config():
    global _config
    config_path = os.path.expanduser(config_file)

    if _config is None:
        with open(config_path, "r") as in_file:
            config_yaml = in_file.read()
        _config = yaml.safe_load(config_yaml)


    return _config

