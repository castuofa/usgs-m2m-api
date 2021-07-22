from dataclasses import dataclass
from typing import ClassVar, List
from .model import Model as BaseModel
from .query import Query as BaseQuery
from .filters import AcquisitionFilter, SpatialFilter
from . import scene


@dataclass
class DatasetModel(BaseModel):
    datasetId: str = None

    datasetAlias: str = None
    abstractText: str = None
    acquisitionStart: str = None
    acquisitionEnd: str = None
    catalogs: list = None
    collectionName: str = None
    collectionLongName: str = None
    datasetAlias: str = None
    datasetCategoryName: str = None
    dataOwner: str = None
    dateUpdated: str = None
    doiNumber: str = None
    ingestFrequency: str = None
    keywords: str = None
    legacyId: str = None
    sceneCount: str = None
    spatialBounds: str = None
    temporalCoverage: list = None
    supportCloudCover: bool = None
    supportDeletionSearch: bool = None

    _bulk_products: list = None

    # @property
    # def bulk_products(self):
    #     datasetName = self.datasetAlias
    #     if not datasetName:
    #         raise AttributeError("Dataset Name is required")

    #     if not self._bulk_products:
    #         self._bulk_products = DatasetBulkProducts(
    #             datasetName=datasetName
    #         )

    #     return self._bulk_products

    def scenes(self, *args, **kwargs) -> List[scene.SceneModel]:
        kwargs["datasetName"] = self.datasetAlias
        query = scene.SceneQuery(*args, **kwargs)
        return self.has_many(query)


@dataclass
class DatasetsQuery(BaseQuery):

    _end_point: ClassVar[str] = "dataset-search"
    _model: ClassVar[DatasetModel] = DatasetModel

    datasetName: str = None
    spatialFilter: SpatialFilter = None
    temporalFilter: AcquisitionFilter = None

    catalog: str = None
    categoryId: str = None
    includeMessages: bool = None
    publicOnly: bool = None
    includeUnknownSpatial: bool = None


@dataclass
class DatasetQuery(BaseQuery):
    _end_point: ClassVar[str] = "dataset"
    _model: ClassVar[DatasetModel] = DatasetModel

    datasetName: str = None
    datasetId: str = None

    @property
    def valid(self):
        return self.datasetName or self.datasetId

    def fetch(self) -> DatasetModel:
        """Always return the single instance in this query

        Returns
        -------
        DatasetModel
            The instantiated Model with the data returned from
            the API
        """
        model = self.fetchone()
        return model
