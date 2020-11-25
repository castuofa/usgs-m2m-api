import random
import json
import getpass
import requests

from logging import getLogger
from os import getenv

from dataclasses import dataclass
from typing import List


from .query import Query
from .model import Model
from .queries import *
from .models import DatasetModel, SceneModel


class Api:

    """Primary interface to the Earth Explorer M2M API. This handles
    login, requests, and construction of Models built from Query objects.

    Use Api.login() to get started

    Attributes
    ----------
    log : logging.Logger
        The primary app logger for this Api. Located at 'usgs_api'

    API_KEY : str
        Set by called .login method and used throughout the app.
        default to None

    _STATUS_CODES : dict
        Used for reporting to provide some context to the codes received

    BASE_URL : str
        The primary URL to the Earth Explorer API. Can be set in .env as EE_URL

    SESSION_LABEL : str
        The label used to queue/order downloadable scenes

    """

    log = getLogger('usgs_api')

    API_KEY = None

    _STATUS_CODES = {
        404: "404 Not Found",
        401: "401 Unauthorized",
        400: "General Error"
    }

    BASE_URL = getenv(
        'EE_URL', None) or "https://m2m.cr.usgs.gov/api/api/json/stable"

    SESSION_LABEL = f"m2m-label-{random.getrandbits(32)}"

    def __init__(self, username: str = None, password: str = None):
        if not self.API_KEY:
            Api.login(username, password)

    def datasets(self, *args, **kwargs) -> List[DatasetModel]:
        """An alias to the DatasetsQuery to return a collection
        of DatasetModels

        Returns
        -------
        List[DatasetModel]
            Collection of datasets
        """
        DatasetsQuery._api = self

        return DatasetsQuery(*args, **kwargs) \
            .fetch()

    def dataset(self, *args, **kwargs) -> DatasetModel:
        """Alias to the single dataset Model
        Requires either a datasetName or datasetId to be set

        Returns
        -------
        DatasetModel
            Single identified dataset if exists
        """
        DatasetQuery._api = self

        return DatasetQuery(*args, **kwargs) \
            .fetch()

    def scenes(self, *args, **kwargs) -> List[SceneModel]:
        """Alias to the SceneQuery to allow more convenient
        collecting of scenes

        Returns
        -------
        List[SceneModel]
            Returns a ResultSet of the collected scenes
        """
        SceneQuery._api = self
        return SceneQuery(*args, **kwargs) \
            .fetch()

    @classmethod
    def login(cls, username: str = None, password: str = None):
        """Allows for three options to acquire the API key from EE
        1. Directly pass the keyword arguments for username/password
        2. If neither are provided, the environment variables for EE_USER
           and EE_PASS are checked (or from .env file if exists)
        3. Direclty prompting the user if 1 or 2 results in None

        Parameters
        ----------
        username : str, optional
            Earth Explorer username with M2M access, by default None
        password : str, optional
            Earth Explorer password, by default None

        Returns
        -------
        Api
            A static Api class with the API key persisted
        """

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

        if not username or not password:
            raise ValueError("Username or Password must be defined")

        cls.API_KEY = cls.request(login_url, login_parameters)

        return cls()

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
            # We got a paginated result
            result = query._model(**result, _api=cls, _query=query)
        else:
            result = cls._build_result(result, query)
        return result

    @classmethod
    def fetchone(cls, query: Query) -> Model:
        """Alias to fetch() class method that returns the first
        indexed value of the collected result. Mostly used for
        convenience as the API will always return a list

        Parameters
        ----------
        query : Query
            Instance of the Query to be matched against

        Returns
        -------
        Model
            A single instance of a model/dataclass that is matched
            with the Query instance
        """
        data = cls.fetch(query)
        if isinstance(data, list):
            return data[0]
        return data

    @classmethod
    def request(cls,
                url: str,
                data: dict = None,
                json_data: str = None,
                api_key: str = None):
        """The primary request builder for the Earth Explorer M2M API
        This is often called internall from the Api class handler, but
        may also be used directly as needed for more customized requests

        Parameters
        ----------
        url : str
            The full URL to the usgs endpoint (often concatenated from Api.BASE_URL)
        data : dict, optional
            The post data to be used in the query. Either data or
            json_data must be set. by default None
        json_data : str, optional
            The post data to be used in the query. Either data or
            json_data must be set. by default None
        api_key : str, optional
            The EE api key obtained from Api.login. by default None

        Returns
        -------
        [type]
            [description]
        """

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
        """Usually called from the Api.request method to report response codes

        Parameters
        ----------
        code : str
            The response code from EE
        message : str
            Response method from EE
        url : str, optional
            URL endpoint accessed that provided the code/response, by default None

        Raises
        ------
        SystemExit
            As the end point failed in this case, the app is halted
        """
        cls.log.error(
            f"Error | Url: {url} | Code: {code} | Returned: {message}"
        )

        raise SystemExit(1)

    @classmethod
    def _build_result(cls, results, query: Query):
        """When the result contains a single list of items, this is used to build
        the list of Models

        Parameters
        ----------
        results : list
            List of dict items returned from the API
        query : Query
            The Query object used to obtain the appropriate Model object

        Returns
        -------
        list
            List of instantiated Models for the results
        """
        return [query._model(**item, _api=cls, _query=query) for item in results]
