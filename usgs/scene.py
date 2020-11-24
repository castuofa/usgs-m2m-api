from dataclasses import dataclass
from typing import ClassVar, List
from .model import (
    Model as BaseModel
)
from .query import (
    Query as BaseQuery,
)
from .filters import (
    SceneFilter
)


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


@dataclass
class SceneQuery(BaseQuery):
    _end_point: ClassVar[str] = "scene-search"
    _model: ClassVar[SceneModel] = SceneModel

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
