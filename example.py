from dotenv import load_dotenv
from datetime import date
from usgs import Api

from usgs.filters import AcquisitionFilter, SceneFilter, SpatialMbr


if __name__ == "__main__":
    # Load env variables
    load_dotenv()

    primary_dataset = "sentinel_2a"

    # Instantiate the Usgs API
    api = Api()

    # Create a Scene filter with an acquisition filter
    scene_filter = SceneFilter(
        acquisitionFilter=AcquisitionFilter(
            start=date(2019, 5, 24), end=date(2019, 5, 31)
        ),
        spatialFilter=SpatialMbr(
            lowerLeft=SpatialMbr.make_point(35.3070, -94.6393),
            upperRight=SpatialMbr.make_point(35.5104, -94.1226),
        ),
    )

    # Prep the dataset
    dataset = api.dataset(datasetName=primary_dataset)

    # Get a scene cursor using the filter
    scene_cursor = dataset.scenes(sceneFilter=scene_filter)

    # Capture only those available for download
    scenes = scene_cursor.downloadable

    # Collect more scenes using the scene cursor
    while scene_cursor.has_more:
        scenes += scene_cursor.next().downloadable

    # Enqueue the scenes
    api.download(scenes)

    # Start the download with the extraction flag
    api.start_download(extract=True)
