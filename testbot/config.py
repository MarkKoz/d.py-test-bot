import logging
from pathlib import Path

import yaml

_log = logging.getLogger(__name__)
_CONFIG_PATH = "config.yml"
_SUFFIX_KEYS = {
    "category": "categories",
    "channel": "text_channels",
    "role": "roles",
    "voice": "voice_channels",
    "webhook": "webhooks",
}


def _get_config_objects(bot):
    for name, module in bot.extensions.items():
        for obj in vars(module).values():
            is_class = isinstance(obj, type)
            if is_class and obj.__name__ == "Config" and obj.__module__ == module.__name__:
                yield obj


def _read_config(path: str):
    path = Path(path)
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)


def load_config(bot, path: str = _CONFIG_PATH):
    user_config = _read_config(path)
    if not user_config:
        _log.info(f"No config found at path {path!r}")
        return

    for obj in _get_config_objects(bot):
        # TODO: throw a warning for unset attributes (i.e. only have a type annotation)?
        for name in vars(obj):
            if name.startswith("_"):
                continue  # Skip private attributes.

            # Split to get the suffix, which may determine where to find the config value.
            split_name = name.rsplit("_", 1)

            try:
                if len(split_name) > 1 and (key := _SUFFIX_KEYS.get(split_name[1])):
                    # Look for the value under the corresponding guild key for the suffix.
                    guild = user_config["guild"] or {}  # Avoids TypeErrors when it's None.
                    category = guild[key] or {}
                    new_value = category[split_name[0]]
                else:
                    # All other attributes are considered specific to that extension.
                    category = user_config[obj.__module__] or {}
                    new_value = category[name]
            except KeyError:
                _log.debug(f"No config value found for {obj.__module__}.{name}; keep the default")
                pass
            else:
                _log.debug(f"Set {obj.__module__}.{name} to {new_value!r}")
                setattr(obj, name, new_value)
