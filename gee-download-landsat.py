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
    

# Define the Landsat image collection and date range of interest
collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')
start_date = ee.Date('2022-01-01')
end_date = ee.Date('2022-01-31')

# Define the ROI as a point, polygon, or other geometry
roi = ee.Geometry.Point(-122.41, 37.74).buffer(500)

# Filter the image collection by date and ROI
filtered_collection = collection.filterDate(start_date, end_date).filterBounds(roi)

# Select the first image in the filtered collection
image = ee.Image(filtered_collection.first())



# Get the image ID and band names
image_id = image.id()
band_names = image.bandNames().getInfo()

print(band_names)
exit()
# Set the output file path
output_file_path = f'{image_id}.tif'

# Define the export parameters
export_params = {
    'image': image,
    'description': image_id,
    'scale': 30,
    'region': roi,
    'fileFormat': 'GeoTIFF',
}

# Export the image to a file on your local machine
task = ee.batch.Export.image.toDrive(export_params)
task.start()

# Wait for the export to finish
while task.active():
    pass

# Check if the export completed successfully
if task.status()['state'] == 'COMPLETED':
    # Download the exported file to your local machine
    download_url = task.status()['asset_url']
    os.system(f'wget -O {output_file_path} "{download_url}"')
