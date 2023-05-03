"""Demonstrates the ee.data.makeDownloadUrl method."""

import io
import requests
import os
import ee
import json
from ee.ee_exception import EEException
from dotenv import load_dotenv
# Load the configuration variables from the .env file
load_dotenv()

private_key_file_path = os.getenv('GEE_SERVICE_ACCOUNT_PATH')

def geeAuthCredentials():
    #// todo - setup env for gee auth path to json service account file
    with open(private_key_file_path,  'r') as file:
        data = json.load(file)
    return data

private_key_json = geeAuthCredentials()
service_account = private_key_json['client_email']

try:
    credentials = ee.ServiceAccountCredentials(service_account, private_key_file_path)
    ee.Initialize(credentials)
except EEException as e:
    print(str(e))

# A Sentinel-2 surface reflectance image.
img = ee.Image('COPERNICUS/S2_SR/20210109T185751_20210109T185931_T10SEG')

# A small region within the image.
region = ee.Geometry.BBox(-122.0859, 37.0436, -122.0626, 37.0586)

# Image chunk as a NumPy structured array.
import numpy
download_id = ee.data.getDownloadId({
    'image': img,
    'bands': ['B3', 'B8', 'B11'],
    'region': region,
    'scale': 20,
    'format': 'NPY'
})
response = requests.get(ee.data.makeDownloadUrl(download_id))
data = numpy.load(io.BytesIO(response.content))
# print(data)
# print(data.dtype)

# Single-band GeoTIFF files wrapped in a zip file.
download_id = ee.data.getDownloadId({
    'image': img,
    'name': 'single_band',
    'bands': ['B3', 'B8', 'B11'],
    'region': region
})

# Download the file.
response = requests.get(ee.data.makeDownloadUrl(download_id))
print(response.content)
with open('single_band.zip', 'wb') as fd:
  fd.write(response.content)