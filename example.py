from dotenv import load_dotenv
from datetime import date
from usgs import Api

from usgs.filters import TemporalFilter, SceneFilter


if __name__ == "__main__":
    # Load env variables
    load_dotenv()

    # Instantiate the Usgs API
    api = Api()

    # Create a Scene filter with a temporal filter
    scene_filter = SceneFilter(
        temporalFilter=TemporalFilter(
            startDate=date(2019, 5, 24), endDate=date(2019, 5, 31)
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
