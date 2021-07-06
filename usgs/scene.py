from dataclasses import dataclass
from typing import ClassVar, List
from .model import Model as BaseModel
from .download import (
    DownloadModel,
    DownloadOptionModel,
    DownloadOptionQuery,
    DownloadRequestQuery,
)
from .query import (
    Query as BaseQuery,
)
from .filters import SceneFilter


@dataclass
class SceneModel(BaseModel):
    browse: list = None
    cloudCover: int = None
    entityId: str = None
    displayId: str = None
    options: dict = None
    metadata: list = None
    selected: dict = None
    publishDate: str = None
    spatialBounds: dict = None
    spatialCoverage: dict = None
    temporalCoverage: dict = None
    orderingId: str = None
    hasCustomizedMetadata: bool = None

    @property
    def datasetName(self):
        return self._query.datasetName if self._query else None

    @property
    def download_available(self):
        """Alias to the download setting in options. This
        may need to be changed in future API changes as the docs
        say this should be called on download-options with entityId.
        Currently this is reflected in this dict object.

        Returns
        -------
        bool
            Boolean whether download is available
        """
        return self.options.get("download", False) and self.options.get("bulk", False)

    def download_options(self) -> DownloadOptionModel:
        """Method to query download availability

        Returns
        -------
        DownloadOptionModel
        """
        return self.api.fetchone(
            DownloadOptionQuery(datasetName=self.datasetName, entityIds=[self.entityId])
        )


@dataclass
class SceneResultSet(BaseModel):
    results: List[SceneModel] = None
    recordsReturned: int = None
    totalHits: int = None
    numExcluded: int = None
    startingNumber: int = None
    nextRecord: int = None
    totalHitsAccuracy: str = None
    isCustomized: bool = None

    def __post_init__(self):
        if self.results:
            results = self.results
            self.results = []
            for result in results:
                self.results.append(
                    SceneModel(**result, _api=self._api, _query=self._query)
                )

    @property
    def datasetName(self):
        return self._query.datasetName if self._query else None

    def __len__(self):
        return len(self.results)

    def next(self):
        if self.totalHits <= self._query.startingNumber:
            return []
        self._query.startingNumber += self._query.maxResults
        self._query._api = self._api
        # return self._api.fetch(self._query)
        return self._query.fetch()

    def download_options(self) -> List[DownloadOptionModel]:
        """Method to query download availability

        Returns
        -------
        List[DownloadOptionModel]
            Collection of Download Option Models
        """
        entityIds = [scene.entityId for scene in self.results]
        return self.api.fetch(
            DownloadOptionQuery(datasetName=self.datasetName, entityIds=entityIds)
        )

    def queue(self):
        download_options = self.download_options()
        downloads = map(
            lambda option: DownloadModel(entityId=option.entityId, productId=option.id),
            filter(lambda option: option.available, download_options),
        )
        download_query = DownloadRequestQuery(
            downloads=list(downloads), label=self._api.SESSION_LABEL
        )
        print(download_query)
        self._api.queue(download_query, self)

        return self

    def __getitem__(self, key):
        return self.results[key]


@dataclass
class SceneQuery(BaseQuery):
    _end_point: ClassVar[str] = "scene-search"
    _model: ClassVar[SceneResultSet] = SceneResultSet

    datasetName: str
    sceneFilter: SceneFilter = None

    sortField: str = None

    # 'ASC' or 'DESC'
    sortDirection: str = None

    compareListName: str = None
    bulkListName: str = None
    orderListName: str = None
    excludeListName: str = None
    includeNullMetadataValues: bool = None

    # 'full' or 'summary'
    metadataType: str = "full"

    maxResults: int = 100
    startingNumber: int = 1
