import json
import getpass

import requests

from logging import getLogger
from os import getenv

from dataclasses import dataclass, field
from typing import ClassVar, Callable, List, Any

from . import (
    utilities
)


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


@dataclass
class Model:
    """Base Model abstract. Should be used as base class when
    defining models
    """

    def to_dict(self):
        return utilities.asdict(self)

    def has_many(self, query: Query):
        return Api.fetch(query)


@dataclass
class Api:

    log = getLogger('usgs_api')

    API_KEY = None

    _STATUS_CODES = {
        404: "404 Not Found",
        401: "401 Unauthorized",
        400: "General Error"
    }

    BASE_URL = getenv(
        'EE_URL', None) or "https://m2m.cr.usgs.gov/api/api/json/stable"

    def __init__(self, username: str = None, password: str = None):
        Api.login(username, password)

    @classmethod
    def login(cls, username: str = None, password: str = None):

        username = username or \
            getenv('EE_USER', None) or \
            input("Please enter username > ")

        password = password or \
            getenv('EE_PASS', None) \
            or getpass.getpass("Please enter EE password > ")

        login_url = f"{cls.BASE_URL}/login"

        login_parameters = {
            'username': username,
            'password': password
        }

        cls.API_KEY = cls.request(login_url, login_parameters)

        return cls

    @classmethod
    def fetch(cls, query: Query) -> List[Model]:
        """Fetch the provided instantiated Query object

        Parameters
        ----------
        query : Query
            The instantiated Query object

        Returns
        -------
        List[Model]
            Returns a list of instantiated Models
        """
        result = cls.request(
            query.endpoint(cls.BASE_URL),
            data=query.to_dict()
        )

        if isinstance(result, dict):
            result = cls._build_result_set(result, query)
        else:
            result = cls._build_result(result, query)
        return result

    @classmethod
    def fetchone(cls, query: Query) -> Model:
        return cls.fetch(query)[0]

    @classmethod
    def request(cls, url: str, data: dict = None, json_data: str = None, api_key: str = None):

        api_key = api_key or cls.API_KEY

        post_data = json.dumps(data) if data else json_data

        request = requests.post(
            url,
            post_data,
            headers={'X-Auth-Token': api_key} if api_key else {}
        )

        # Anyone home?
        if request.status_code is None:
            cls._exit_with_message(None, "No output from service", url)

        try:
            response = json.loads(request.text)

            # Verbose server side error
            error_code = response.get('errorCode', None)
            error_message = response.get('errorMessage', None)

            # Status code errors
            error_message = cls._STATUS_CODES.get(request.status_code, None)
            if error_message:
                error_code = request.status_code

        except Exception as e:
            request.close()
            cls._exit_with_message(None, f'{url} | {e}')

        else:
            if error_code or error_message:
                cls._exit_with_message(error_code, error_message, url)
            return response.get('data', None)

    @classmethod
    def _exit_with_message(cls, code, message: str, url: str = None):

        cls.log.error(
            f"Error | Url: {url} | Code: {code} | Returned: {message}"
        )

        raise SystemExit(1)

    @classmethod
    def _build_result_set(cls, results, query):
        items = []
        for item_data in results.get('results', []):
            items.append(query._model(**item_data))
        results['results'] = items
        result_set = ResultSet(**results)
        result_set._query_builder = query
        query.totalResults = result_set.totalHits

        return result_set

    @classmethod
    def _build_result(cls, results, query: Query):
        return [query._model(**item) for item in results]


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
