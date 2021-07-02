from dataclasses import dataclass, field
from typing import ClassVar, List
from .model import (
    Model as BaseModel
)
from .query import (
    Query as BaseQuery,
)


@dataclass
class DownloadModel(BaseModel):
    entityId: str = None
    productId: str = None


@dataclass
class Download(BaseModel):
    downloadId: str = None
    collectionName: str = None
    datasetId: str = None
    displayId: str = None
    entityId: str = None
    eulaCode: str = None
    filesize: str = None
    label: str = None
    productCode: str = None
    productName: str = None
    statusCode: str = None
    statusText: str = None
    url: str = None
    _saved: bool = False


@dataclass
class DownloadRetrieveModel(BaseModel):
    available: List[Download] = None
    queueSize: int = 0
    requested: List[Download] = None
    eulas: list = None

    def __post_init__(self):
        self.available = [Download(**item) for item in self.available]
        self.requested = [Download(**item) for item in self.requested]

    @property
    def size(self):
        return len(self.available) + len(self.requested)

    def get_items(self):
        return self.available + self.requested


@dataclass
class DownloadRetrieveQuery(BaseQuery):
    _end_point: ClassVar[str] = "download-retrieve"
    _model: DownloadRetrieveModel = DownloadRetrieveModel

    label: str = None


@dataclass
class DownloadRequestModel(BaseModel):
    failed: list = None
    newRecords: dict = None
    numInvalidScenes: int = None
    duplicateProducts: list = None
    availableDownloads: list = None
    preparingDownloads: list = None
    _current_downloads: DownloadRetrieveModel = None

    def retrieve(self):
        self._current_downloads = self._api.fetch(
            DownloadRetrieveQuery(
                label=self._api.SESSION_LABEL
            )
        )
        if self.duplicateProducts:
            for dupe in self.duplicateProducts:
                print(f"Requesting {self.duplicateProducts[dupe]}")
                duplicate_request = self._api.fetch(
                    DownloadRetrieveQuery(
                        label=self.duplicateProducts[dupe]
                    )
                )
                self._current_downloads.available += duplicate_request.available
                self._current_downloads.requested += duplicate_request.requested

    @property
    def size(self):
        return len(self.availableDownloads) + len(self.preparingDownloads)

    @property
    def requested_ids(self):
        return list(map(lambda download: download['downloadId'], self.availableDownloads)) \
            + list(map(lambda download: download['downloadId'], self.preparingDownloads))

    @property
    def ready(self):
        self.retrieve()
        return self.size == len(self.downloads)

    @property
    def downloads(self):
        return list(filter(lambda download: download.downloadId in self.requested_ids, self._current_downloads.get_items()))


@dataclass
class DownloadRequestQuery(BaseQuery):
    _end_point: ClassVar[str] = "download-request"
    _model: DownloadRequestModel = DownloadRequestModel

    downloads: List[DownloadModel] = None
    label: str = None


@dataclass
class DownloadOptionModel(BaseModel):
    id: str = None
    displayId: str = None
    entityId: str = None
    datasetId: str = None
    available: bool = False
    filesize: int = None
    productName: str = None
    productCode: str = None
    bulkAvailable: bool = False
    downloadSystem: str = None
    secondaryDownloads: list = None


@dataclass
class DownloadOptionQuery(BaseQuery):
    _end_point: ClassVar[str] = "download-options"
    _model: ClassVar[DownloadOptionModel] = DownloadOptionModel

    datasetName: str = None
    entityIds: list = None
    listId: str = None
