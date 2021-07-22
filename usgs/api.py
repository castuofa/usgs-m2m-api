import os
import random
import json
import time
import getpass
import tarfile
import datetime
from os import getenv
from typing import List

import requests
from clint.textui import progress

from usgs.download import DownloadRequestModel, DownloadRequestQuery
from logging import getLogger

from .query import Query
from .model import Model
from .queries import *
from .models import DatasetModel, SceneModel
from .download import (
    DownloadModel,
    DownloadOptionQuery,
    DownloadOptionModel,
    DownloadRequestModel,
    DownloadRequestQuery,
)


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

    log = getLogger("usgs_api")

    API_KEY = None

    _STATUS_CODES = {
        404: "404 Not Found",
        401: "401 Unauthorized",
        400: "General Error",
    }

    BASE_URL = getenv("EE_URL", None) or "https://m2m.cr.usgs.gov/api/api/json/stable"

    SESSION_LABEL = f"m2m-label-{random.getrandbits(32)}"

    DOWNLOAD_QUERIES: List[DownloadRequestModel] = []

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

        return DatasetsQuery(*args, **kwargs).fetch()

    def dataset(self, *args, **kwargs) -> DatasetModel:
        """Alias to the single dataset Model
        Requires either a datasetName or datasetId to be set

        Returns
        -------
        DatasetModel
            Single identified dataset if exists
        """
        DatasetQuery._api = self

        return DatasetQuery(*args, **kwargs).fetch()

    def scenes(self, *args, **kwargs) -> List[SceneModel]:
        """Alias to the SceneQuery to allow more convenient
        collecting of scenes

        Returns
        -------
        List[SceneModel]
            Returns a ResultSet of the collected scenes
        """
        SceneQuery._api = self
        return SceneQuery(*args, **kwargs).fetch()

    @classmethod
    def queue(cls, download_query: DownloadRequestQuery):
        cls.DOWNLOAD_QUERIES.append(cls.fetch(download_query))

    def download(self, scenes: List[SceneModel]):

        data = {}
        for scene in scenes:
            dataset = data.get(scene.datasetName, [])
            dataset.append(scene.entityId)
            data[scene.datasetName] = dataset

        options_results: List[DownloadOptionModel] = []

        for dataset in data.keys():
            options_results.extend(
                self.fetch(
                    DownloadOptionQuery(datasetName=dataset, entityIds=data[dataset])
                )
            )

        downloads = map(
            lambda option: DownloadModel(entityId=option.entityId, productId=option.id),
            options_results,
        )

        download_query = DownloadRequestQuery(
            downloads=list(downloads), label=self.SESSION_LABEL
        )

        self.queue(download_query)

        return self

    def start_download(self, extract: bool = False):
        if self.DOWNLOAD_QUERIES:
            for download_request_model in self.DOWNLOAD_QUERIES:
                # download_request_model.retrieve()
                while not download_request_model.ready:
                    print("Waiting for preparation")
                    time.sleep(5)

                # Save the files
                for download in download_request_model.downloads:
                    self.save(download, extract)

            # Reset the queue
            self.DOWNLOAD_QUERIES = list(
                filter(
                    lambda download_request: download_request._saved is False,
                    self.DOWNLOAD_QUERIES,
                )
            )

    def save(self, download, extract: bool = False):
        print(f"Downloading: {download.url} | {download.entityId}")

        filePath = f"{download.displayId}.tgz"

        with open(filePath, "wb") as fp:
            request = requests.get(download.url, stream=True)

            total_length = int(request.headers.get("content-length"))

            for chunk in progress.bar(
                request.iter_content(chunk_size=1024),
                expected_size=(total_length / 1024) + 1,
            ):
                if chunk:
                    fp.write(chunk)

        download._saved = True

        if extract:
            self._extract_tar(filePath)
            os.unlink(filePath)

    def _extract_tar(self, filePath):
        tar = tarfile.open(filePath, "r")
        print(f"Extracting: {filePath}")
        for item in tar:
            dirpath = os.path.abspath(
                os.path.basename("".join(filePath.split(".")[:-1]))
            )
            tar.extract(item, dirpath)

    @classmethod
    def login(cls, username: str = None, password: str = None):
        """Allows for three options to acquire the API key from EE
        1. Directly pass the keyword arguments for username/password
        2. If neither are provided, the environment variables for EE_USER
           and EE_PASS are checked (or from .env file if exists)
        3. Directly prompting the user if 1 or 2 results in None

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

        username = (
            username or getenv("EE_USER", None) or input("Please enter username > ")
        )

        password = (
            password
            or getenv("EE_PASS", None)
            or getpass.getpass("Please enter EE password > ")
        )

        login_url = f"{cls.BASE_URL}/login"

        login_parameters = {"username": username, "password": password}

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
        result = cls.request(query.endpoint(cls.BASE_URL), data=query.to_dict())

        if isinstance(result, dict):
            # We got a paginated result
            result = query._model(**result, _api=cls, _query=query)
        elif result:
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
    def request(
        cls,
        url: str,
        data: dict = None,
        json_data: str = None,
        api_key: str = None,
        raw: bool = False,
        chunk: bool = False,
        chunk_size: int = 1024,
    ):
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
        raw: bool, optional
            Returns the raw content of the requests (requests.content)
        chunk: bool, optional
            Returns an iterator, relative to the chunk size, for data. This overrides raw behavior
        chunk_size: int, 1024
            If chunk is enabled, this defines the chunk size for the iterator

        Returns
        -------
        [type]
            [description]
        """

        api_key = api_key or cls.API_KEY

        post_data = json.dumps(data, cls=DataTypeEncoder) if data else json_data

        request = requests.post(
            url, post_data, headers={"X-Auth-Token": api_key} if api_key else {}
        )

        # Anyone home?
        if request.status_code is None:
            cls._exit_with_message(None, "No output from service", url)

        try:
            response = json.loads(request.text)

            # Verbose server side error
            error_code = response.get("errorCode", None)
            error_message = response.get("errorMessage", None)

            # Status code errors
            error_message = cls._STATUS_CODES.get(request.status_code, None)
            if error_message:
                error_code = request.status_code

        except Exception as e:
            request.close()
            cls._exit_with_message(None, f"{url} | {e}")

        else:
            if error_code or error_message:
                cls._exit_with_message(error_code, error_message, url)
            if chunk:
                return response.iter_content(chunk_size=chunk_size)
            if raw:
                return response.content
            return response.get("data", None)

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
        cls.log.error(f"Error | Url: {url} | Code: {code} | Returned: {message}")

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


class DataTypeEncoder(json.JSONEncoder):

    """
    A special JSON encoder to produce ISO 8601 formats from datetime objects
    """

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        return super().default(obj)
