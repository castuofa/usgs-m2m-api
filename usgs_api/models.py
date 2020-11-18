from dataclasses import dataclass
from typing import ClassVar, List
from .abstracts import (
    Model as BaseModel
)


@dataclass
class DatasetBulkProduct:
    productCode: str = None
    productName: str = None


@dataclass
class DatasetBulkProducts(BaseModel):
    _end_point: ClassVar[str] = "dataset-bulk-products"

    datasetName: str
