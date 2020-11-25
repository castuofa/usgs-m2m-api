from typing import Any
from dataclasses import dataclass, field


@dataclass
class Relations:
    _api: Any = field(repr=False, default=None)

    _query: Any = field(repr=False, default=None)

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, api_reference):
        self._api = api_reference

    def has_many(self, query):
        return self.api.fetch(query)
