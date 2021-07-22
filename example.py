from dotenv import load_dotenv
from datetime import date
from usgs import Api

from usgs.filters import AcquisitionFilter, SceneFilter


if __name__ == "__main__":
    # Load env variables
    load_dotenv()

    # Instantiate the Usgs API
    api = Api()

    # Create a Scene filter with an acquisition filter
    scene_filter = SceneFilter(
        acquisitionFilter=AcquisitionFilter(
            start=date(1972, 5, 24), end=date(1972, 5, 31)
        )
    )

    # Get a scene cursor using the filter
    scene_cursor = api.dataset(datasetName="corona2").scenes(sceneFilter=scene_filter)

    # Capture only those available for download
    scenes = scene_cursor.downloadable

    # Collect more scenes using the scene cursor
    while len(scenes) < 3:
        scenes += scene_cursor.next().downloadable

    # Enqueue the scenes
    api.download(scenes)

    # Start the download with the extraction flag
    api.start_download(extract=True)
