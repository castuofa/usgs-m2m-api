from dataclasses import dataclass, field
from typing import ClassVar
from .model import (
    Model as BaseModel
)


@dataclass
class DatasetBulkProduct:
    productCode: str = None
    productName: str = None


@dataclass
class DatasetBulkProducts(BaseModel):
    _end_point: ClassVar[str] = "dataset-bulk-products"

    datasetName: str = field(default=None)
