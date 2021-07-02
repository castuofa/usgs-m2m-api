from dataclasses import dataclass, field
from typing import Any, List
from .relations import Relations
from . import utilities


@dataclass
class Model(Relations):
    """Base Model abstract. Should be used as base class when
    defining models
    """

    def to_dict(self):
        """Utility method to convert the dataclass Model to dict

        Returns
        -------
        dict
            dictionary version of the dataclass
        """
        return utilities.asdict(self)

    def download_options(self):
        raise NotImplementedError("Cannot request downloads on this model")
