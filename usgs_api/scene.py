from dataclasses import dataclass
from typing import ClassVar, List
from .abstracts import (
    Query as BaseQuery,
    Model as BaseModel
)
from .filters import (
    SceneFilter
)


@dataclass
class Model(BaseModel):
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


@dataclass
class Query(BaseQuery):
    _end_point: ClassVar[str] = "scene-search"
    _model: ClassVar[Model] = Model

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
