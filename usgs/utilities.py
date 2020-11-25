import json
import getpass
import requests

from dataclasses import (
    asdict as dataclass_to_dict
)


def clean_dataclass_of_private_variables(o: list):
    return dict(filter(lambda field: not field[0].startswith('_'), o))


def asdict(o, skip_empty=False):
    data = dataclass_to_dict(
        o, dict_factory=clean_dataclass_of_private_variables)
    return {
        k: v for k, v in data.items()
        if not (skip_empty and v is None) and not k.startswith('_')
    }
