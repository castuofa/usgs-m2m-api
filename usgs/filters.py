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
    filterType: str = "geojson"
    geoJson: GeoJson = None


@dataclass
class DateRange:
    startDate: datetime.date
    endDate: datetime.date

    @classmethod
    def from_string(cls, startDate, endDate):
        return cls(parse(startDate), parse(endDate))


@dataclass
class IngestFilter:
    """
    Used to apply an ingest filter that limits by the dates the scenes
    were added to the catalog

    Paramters
    ---------
    start : datetime.date
    end : datetime.date
    """

    start: datetime.date
    end: datetime.date = None

    def __post_init__(self):
        if not self.end:
            self.end = datetime.datetime.now()

    @classmethod
    def from_string(cls, start, end):
        return cls(parse(start), parse(end))


@dataclass
class AcquisitionFilter:
    """
    Used to apply a acquisition date filter to scene searches

    For string based searching, use the utility factory AcquisitionFilter.from_string()

    Paramters
    ---------
    start : datetime.date
    end : datetime.date
    """

    start: datetime.date
    end: datetime.date = None

    def __post_init__(self):
        if not self.end:
            self.end = datetime.datetime.now()

    @classmethod
    def from_string(cls, start, end):
        return cls(parse(start), parse(end))


@dataclass
class CloudCoverFilter:
    min: int
    max: int
    includeUnknown: bool = True


@dataclass
class SceneFilter:
    ingestFilter: IngestFilter = None
    spatialFilter: SpatialFilter = None
    acquisitionFilter: AcquisitionFilter = None
    cloudCoverFilter: CloudCoverFilter = None

    # Seasonal Filter is essentially a 1-12 list of months
    seasonalFilter: List[int] = None

    ## TODO: implement factory methods for subfilters
    # scene_filter.acquired(start, end)
    # scene_filter.within_mbr(ll, ur)
    # scene_filter.within_geometry(geojson)
    # scene_filter.season('summer')
