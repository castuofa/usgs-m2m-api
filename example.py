from dotenv import load_dotenv
from usgs import (
    dataset,
    Api
)


if __name__ == "__main__":
    load_dotenv()

    api = Api.login()

    query = dataset.Query(
        datasetName="corona2"
    )

    dataset = api.fetchone(
        query
    )

    corona_scenes = dataset.scenes()

    downloadable_scenes = list(
        filter(lambda scene: scene.options.get('download'), corona_scenes))

    print(downloadable_scenes[0])
