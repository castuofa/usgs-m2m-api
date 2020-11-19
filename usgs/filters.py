import datetime
from dateutil.parser import parse
from typing import List
from dataclasses import dataclass, asdict


@dataclass
class BaseFilter:
    def to_dict(self):
        return asdict(self)


@dataclass
class Point:
    latitude: float
    longitude: float


@dataclass
class SpatialFilter:
    filterType: str = None


@dataclass
class SpatialMbr(SpatialFilter):
    filterType: str = "mbr"
    lowerLeft: Point = None
    upperRight: Point = None


@dataclass
class GeoJson:
    type: str
    coordinates: List[Point]


@dataclass
class SpatialGeojson(SpatialFilter):
    geoJson: GeoJson = None
    filterType: str = "geojson"


@dataclass
class TemporalFilter:
    startDate: datetime.date
    endDate: datetime.date

    @classmethod
    def from_string(cls, startDate, endDate):
        return cls(
            parse(startDate),
            parse(endDate)
        )


@dataclass
class IngestFilter:
    start: datetime.date
    end: datetime.date = None

    @classmethod
    def from_string(cls, start, end):
        return cls(
            parse(start),
            parse(end)
        )


@dataclass
class SceneFilter:
    ingestFilter: IngestFilter
    spatialFilter: SpatialFilter
    temporalFilter: TemporalFilter
    seasonalFilter: List[int] = None
