from dataclasses import dataclass, field
from typing import ClassVar, Any
from . import utilities, model


@dataclass
class Query:
    """Base Query object that handles utility type methods

    Raises
    ------
    NotImplementedError
        Thrown when method doesn't exist or wasn't overridden
        by inherited object
    """

    _end_point: ClassVar[str] = None
    _model: ClassVar[str] = None
    _api: ClassVar[Any] = None

    totalResults: int = field(init=False, repr=False, default=0)

    @property
    def valid(self):
        return True

    def to_dict(self):
        return utilities.asdict(self, skip_empty=True)

    def endpoint(self, base_url: str):
        if not base_url and not self._end_point:
            raise NotImplementedError("Endpoint does not exist")

        if base_url[-1] == '/':
            base_url = base_url[:-1]

        return f"{base_url}/{self._end_point}"

    def fetch(self):
        if not self._api:
            raise ValueError("API must be instantiated first")

        return self._api.fetch(self)

    def fetchone(self) -> model.Model:
        return self._api.fetchone(self)
