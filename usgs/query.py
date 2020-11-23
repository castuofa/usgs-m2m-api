from dataclasses import dataclass, field
from typing import ClassVar
from . import utilities


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

    totalResults: int = field(init=False, repr=False, default=0)

    def to_dict(self):
        return utilities.asdict(self, skip_empty=True)

    def endpoint(self, base_url: str):
        if not base_url and not self._end_point:
            raise NotImplementedError("Endpoint does not exist")

        if base_url[-1] == '/':
            base_url = base_url[:-1]

        return f"{base_url}/{self._end_point}"
