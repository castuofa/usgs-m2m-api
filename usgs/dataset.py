from dataclasses import dataclass, field
from typing import ClassVar, List
from .model import Model as BaseModel
from .query import Query as BaseQuery
from .filters import (
    SpatialFilter,
    TemporalFilter
)
from . import scene


@dataclass
class Model(BaseModel):
    datasetId: str = None

    datasetAlias: str = None
    abstractText: str = None
    acquisitionStart: str = None
    acquisitionEnd: str = None
    catalogs: list = None
    collectionName: str = None
    collectionLongName: str = None
    datasetId: str = None
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

    def scenes(self, *args, **kwargs) -> List[scene.Model]:
        kwargs['datasetName'] = self.datasetAlias
        query = scene.Query(*args, **kwargs)
        return self.has_many(query)


@dataclass
class Query(BaseQuery):

    _end_point: ClassVar[str] = "dataset-search"
    _model: ClassVar[Model] = Model

    datasetName: str = None
    spatialFilter: SpatialFilter = None
    temporalFilter: TemporalFilter = None

    catalog: str = None
    categoryId: str = None
    includeMessages: bool = None
    publicOnly: bool = None
    includeUnknownSpatial: bool = None
