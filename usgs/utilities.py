import json
import getpass
import requests

from dataclasses import asdict as dataclass_to_dict


def asdict(o, skip_empty=False):
    data = dataclass_to_dict(o)
    return {
        k: v for k, v in data.items()
        if not (skip_empty and v is None)
    }
