from dotenv import load_dotenv
from datetime import date
from usgs import dataset, scene, Api

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
    scene_cursor = api.dataset(datasetName="corona2").scenes()

    scenes = scene_cursor.downloadable

    while len(scenes) < 3:
        scenes += scene_cursor.next().downloadable

    api.download(scenes)

    print(api.DOWNLOAD_QUERIES)

    api.start_download(extract=True)

    print(api.SESSION_LABEL)
