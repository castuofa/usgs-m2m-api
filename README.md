# USGS Python API

An object oriented wrapper around the USGS Earth Explorer JSON API (v1.5.x). The primary objective of this API is to provide a convenient method of requesting and downloading scenes from EE datasets, including robust metadata where available.

## API Documentation
https://cast.git-pages.uark.edu/transmap-hub/usgs/usgs/

## Prerequisites
- Must have an Earth Explorer account: https://earthexplorer.usgs.gov
- The EE account must have M2M accesss, requested here: https://ers.cr.usgs.gov/profile/access (you will need to wait for approval)

## Installation and Setup

### Three methods for using your username and password
1. Using a `.env` file
```
EE_USER="user_name"
EE_PASS="user_pass"
```
2. Set your environment variables manually
```bash
$ export EE_USER="user_name"
$ export EE_PASS="user_pass"
```
3. During each execution you will be prompted for your user:pass if one of the above two options are not set
4. Hard code within script (not recommended) - see below

### Installation (development)

```python
$ pipenv install
$ pipenv run python ./example.py
```

### Basic API structure
To query a specific item, like a `dataset` or a `scene`, you need to construct a `Query` object from that namespace (`dataset.Query`, `scene.Query`) and pass that to the `Api` with either a `fetch` or `fetchone`. This will return a `Model` or `List[Model]` of that type (`dataset.Model`, `scene.Model`)


_Initialize the API_
```python
from usgs_api import Api
api = Api.login()
### If you want to directly type your user:password you can use
api = Api(username="user_name", password="password")
```
_Query a dataset by name_
```python
dataset = api.dataset(datasetName="corona2")
```
_Start a scene cursor with a list of scenes_
```python
scene_cursor = dataset.scenes()
```
_Collect only available scenes to queue for download_
```python
downloadable = scene_cursor.downloadable
```
_Iterate the cursor to collect more scenes_
```python
downloadable += scene_cursor.next().downloadable
```
_Enqueue the scenes for download from the Api_
```python
api.download(scenes)
```
_Start the download and automate the extraction_
```python
api.start_download(extract=True)
```




