from dataclasses import dataclass, field
from typing import ClassVar
from .model import (
    Model as BaseModel
)
from .dataset import DatasetModel
from .scene import SceneModel

__all__ = [
    'DatasetModel',
    'SceneModel'
]


@dataclass
class DatasetBulkProduct:
    productCode: str = None
    productName: str = None


@dataclass
class DatasetBulkProducts(BaseModel):
    _end_point: ClassVar[str] = "dataset-bulk-products"

    datasetName: str = field(default=None)
