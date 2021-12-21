import os
import tarfile
from time import sleep
from typing import List, Union
from queue import Queue

import requests
from clint.textui import progress

from .api import Api
from .dataset import DatasetModel
from .scene import SceneModel
from .download import (
  DownloadRequestModel,
  DownloadOptionQuery,
  DownloadOptionModel,
  DownloadModel,
  DownloadRequestQuery,
  DownloadRetrieveModel,
  DownloadRetrieveQuery
)


class DownloadManager:

    _queue_state: dict = {}

    _option_models: dict = {}

    _original_request: DownloadRequestModel = None

    _label: str = None

    _requested: dict = {}

    _available: dict = {}

    _downloading: dict = {}

    _completed: dict = {}

    _failed: dict = {}

    _labels: List[str] = []


    def __init__(self, api: Api, dataset: Union[DatasetModel, str], path: str = "/", post_process: bool = False, cleanup: bool = False):

        self.dataset = dataset if isinstance(dataset, DatasetModel) else self.api.dataset(dataset)

        if not self.dataset:
            raise ValueError(f"{dataset} was not found in the USGS API")

        self.api = api

        self._label = self.api.SESSION_LABEL

        self._scenes_to_download = []

        self.post_process = post_process

        self.cleanup = cleanup

    def add(self, scene: Union[SceneModel, str]) -> "DownloadManager":

        # Only need the entity id
        scene = scene.entityId if isinstance(scene, SceneModel) else scene

        # Fetch the download capabilities
        options_result: List[DownloadOptionModel] = self.api.fetch(
            DownloadOptionQuery(datasetName=self.dataset.datasetAlias, entityIds=[scene])
        )

        for option_result in options_result:
          self._option_models[option_result.entityId] = option_result

        return self

    def add_scenes(self, scenes):
        # Fetch the download capabilities
        options_result: List[DownloadOptionModel] = self.api.fetch(
            DownloadOptionQuery(datasetName=self.dataset.datasetAlias, entityIds=scenes)
        )

        print(options_result)

        for option_result in options_result:
          self._option_models[option_result.entityId] = option_result

        return self

    def prepare(self):
        # Collect the added option models for the request
        option_models: List[DownloadOptionModel] = self._option_models.values()

        # Setup the initial queue
        self._requested.update(self._option_models)

        # Prepare the download models to post in the request query
        download_models = map(
            lambda option_model: DownloadModel(entityId=option_model.entityId, productId=option_model.id),
            option_models
        )

        # Make the download request with our current batch
        download_query = DownloadRequestQuery(downloads=list(download_models), label=self.api.SESSION_LABEL)

        self._labels.append(self.api.SESSION_LABEL)

        # Submit the download request of the batch
        self._original_request = self.api.fetch(download_query)

        # Apparently if request failures occur, it's at this point
        # Let's clear the failed requests from the requested queue
        for _failed in self._original_request.failed:
            self._requested.pop(_failed.get('entityId'))
            self._failed[_failed.get('entityId')] = _failed.get('errorMessage')

        print(self._original_request)

        if not isinstance(self._original_request.duplicateProducts, list):
            # Apparently the behavior of the API changes to return an empty list if no dupes
            # Otherwise it returns an object - fun fun
            self._labels += list(self._original_request.duplicateProducts.values())

    def start(self):

        self.prepare()

        self.collect_downloads()

        while self._requested or self._downloading:

            if self._downloading:
                print("Doing downloads")
                self.do_downloads()
            else:
                print("Waiting for preparation")
                sleep(10)
            self.collect_downloads()

        if self._failed:
            print("Some scenes failed to download")
            print(self._failed)

    def collect_downloads(self):

        for label in self._labels:

            # Get current status
            api_queue: DownloadRetrieveModel = self.api.fetch(
                DownloadRetrieveQuery(label=label)
            )

            for available in api_queue.available:

                entity_id = available.entityId

                if entity_id in self._requested.keys():
                    self._requested.pop(entity_id)

                if entity_id in self._completed.keys() or entity_id in self._downloading.keys():
                    continue

                self._downloading[entity_id] = available

            for requested in api_queue.requested:

                entity_id = requested.entityId

                self._requested[entity_id] = requested

                if entity_id in self._completed.keys() or entity_id in self._downloading.keys():
                    self._requested.pop(entity_id)
                    continue

    def do_downloads(self):

        download_ids = list(self._downloading.keys())[::]

        for entity_id in download_ids:
            download = self._downloading.pop(entity_id)

            try:
                self.save(download)
            except Exception as exc:
                self._failed[entity_id] = exc
            else:
                self._completed[entity_id] = download

    def save(self, download):
        print(f"Downloading: {download.url} | {download.entityId}")
        # return True

        file_types = {"image/tiff": "tif", "application/zip": "zip"}

        filePath = f"{download.displayId}"

        request = requests.get(download.url, stream=True)

        total_length = int(request.headers.get("content-length"))
        file_type = request.headers.get("content-type")

        extension = file_types.get(file_type, "tgz")
        filePath = f"{filePath}.{extension}"

        with open(filePath, "wb") as fp:

            for chunk in progress.bar(
                request.iter_content(chunk_size=1024),
                expected_size=(total_length / 1024) + 1,
            ):
                if chunk:
                    fp.write(chunk)

        download._saved = True

        extract_router = {"tif": self._tiff, "zip": self._zip, "tgz": self._extract_tar}

        if self.post_process:
            route = extract_router.get(extension, self._extract_tar)
            route(filePath)

    def _zip(self, filePath):
        pass

    def _tiff(self, filePath):
        pass

    def _extract_tar(self, filePath):
        tar = tarfile.open(filePath, "r")
        print(f"Extracting: {filePath}")
        for item in tar:
            dirpath = os.path.abspath(
                os.path.basename("".join(filePath.split(".")[:-1]))
            )
            tar.extract(item, dirpath)

        if self.cleanup:
            os.unlink(filePath)

