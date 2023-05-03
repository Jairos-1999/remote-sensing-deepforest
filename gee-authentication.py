# system imports
import os
import json
import time

# dependencies
import ee
from ee.ee_exception import EEException
import requests
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
    
    
    
with open('./geojson/dzalanyama.geojson',  'r') as file:
    geojson = json.load(file)
    
# print(type(geojson))
# Define a region of interest
# roi = ee.Geometry.Point([-14.29643667, 33.49098064])
geojsonObject = {
  "type": "Polygon",
  "coordinates": [
    [
      [
        -122.085,
        37.423
      ],
      [
        -122.092,
        37.424
      ],
      [
        -122.085,
        37.418
      ],
      [
        -122.085,
        37.423
      ]
    ]
  ]
}
roi = ee.Geometry(geojsonObject)
# print(roi)
# exit()
# Define the Landsat 8 collection
landsat = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')

# Filter the collection by date and region
landsat = landsat.filterDate('2023-04-01', '2023-04-15').filterBounds(roi).sort('CLOUD_COVER').first()
img = ee.Image('COPERNICUS/S2_SR/20210109T185751_20210109T185931_T10SEG')
# print(image)
# exit()
# Download the image and save it to a directory
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
output_file = os.path.join(output_dir, 'landsat_image')

# Define the download parameters
params = {
    'image': ee.Image(landsat),
    'description': 'landsat_image',
    'scale': 30,
    'crs': 'EPSG:4326',
    'region': roi.getInfo()['coordinates'],
    'fileFormat': 'GeoTIFF',
    # 'folder': output_file
}

print(params)
# print(img)
download_id = ee.data.getDownloadId({
    'image': img,
    'description': 'landsat_image',
    'scale': 20,
    'format': 'NPY',
    'crs': 'EPSG:4326',
    'region': roi,
    # 'folder': output_file
})

# Download the file.
response = requests.get(ee.data.makeDownloadUrl(download_id))
print(response)

# Get the image URL
url = img.getDownloadURL({
    'scale': 30,
    'crs': 'EPSG:4326',
    'region': roi.getInfo()['coordinates']
})

# Print the URL
# print(url)

task = ee.batch.Export.image.toDrive(**params)
task.start()

# Wait for the task to complete
print('Downloading Image...')
while task.active():
    time.sleep(1)
    # print(task.status()['state'])
# Wait for the export to finish
# while task.active():
#     pass

# download_url = task.status()['asset_url']
print(task.status())
# Check if the export completed successfully
if task.status()['state'] == 'COMPLETED':
    print('Image downloaded to ' + output_file)
    # Download the exported file to your local machine
    download_url = task.status()['asset_url']
    print(download_url)
    os.system(f'wget -O {output_file} "{download_url}"')