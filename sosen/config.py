from pathlib import Path
import os
import yaml

_config = None

config_file = "~/.sosen/config.yml"

def configure(**kwargs):
    global _config

    get_config()

    _config.update(kwargs)

    config_path = os.path.expanduser(config_file)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as out_file:
        out_file.write(yaml.dump(_config))


def get_defaults():
    return {
        "endpoint": "https://dev.endpoint.mint.isi.edu/sosen/query",
        "object_prefix": "https://w3id.org/okn/i/",
    }


class SosenConfigurationException(Exception):
    pass


def get_config():
    global _config
    config_path = os.path.expanduser(config_file)

    if _config is None:
        if os.path.exists(config_path):
            with open(config_path, "r") as in_file:
                config_yaml = in_file.read()
            _config = yaml.safe_load(config_yaml)

            for key, default_value in get_defaults().items():
                if key not in _config:
                    _config[key] = default_value

        else:
            _config = get_defaults()

    return _config

