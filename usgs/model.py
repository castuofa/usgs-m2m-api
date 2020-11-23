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


@dataclass
class ResultSet:
    results: List[Model]
    recordsReturned: int
    totalHits: int
    numExcluded: int
    startingNumber: int
    nextRecord: int

    _query_builder: Any = field(init=False, repr=False, default=None)

    def next(self):
        if self.totalHits <= self._query_builder.startingNumber:
            return []
        self._query_builder.startingNumber += self._query_builder.maxResults
        return self._query_builder.get()

    def __getitem__(self, key):
        return self.results[key]
