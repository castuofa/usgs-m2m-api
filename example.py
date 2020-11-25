from dotenv import load_dotenv
from usgs import (
    dataset,
    Api
)


if __name__ == "__main__":
    load_dotenv()

    # api = Api.login()

    # query = dataset.DatasetsQuery(
    #     datasetName="corona2"
    # )

    # dataset = api.fetchone(
    #     query
    # )

    # corona_scenes = dataset.scenes()

    # downloadable_scenes = list(
    #     filter(lambda scene: scene.options.get('download'), corona_scenes))

    # print(downloadable_scenes[0])

    api = Api()
    print(api.dataset(datasetName="corona2").scenes().download_options())

    # usgs_api = Api()
    # print(usgs_api.datasets(datasetName="corona2").fetch())
    # print(usgs_api.dataset(datasetName="corona2").fetchone().scenes)
