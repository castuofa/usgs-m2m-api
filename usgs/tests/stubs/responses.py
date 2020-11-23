import json
from os.path import basename, realpath, dirname
from glob import glob

PATHS = glob(f"{dirname(realpath(__file__))}/*.json")

SAMPLES = {}

for stub in PATHS:
    endpoint = basename(stub).split('.')[0]
    try:
        SAMPLES[endpoint] = json.load(open(stub, 'r'))
    except Exception as e:
        print(f"{stub}")
        print(e)
