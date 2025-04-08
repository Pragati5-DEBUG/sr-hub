import streamlit as st
import ee
import os
import geemap
from datetime import datetime
from PIL import Image
import numpy as np
import tifffile
import io

# Initialize Earth Engine
def authenticate_and_initialize():
    """Handles GEE authentication and initialization"""
    try:
        ee.Initialize()
        print("Earth Engine initialized successfully!")
    except Exception:
        ee.Authenticate()
        ee.Initialize()
        print("Earth Engine initialized successfully!")

authenticate_and_initialize()

# Function to process satellite image collections
def process_collection(collection, name, point, region, start_date, end_date):
    """Processes an individual collection"""
    if 'SENTINEL' in name:
        filtered = collection.filterBounds(point) \
                             .filterDate(start_date, end_date) \
                             .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                             .sort('CLOUDY_PIXEL_PERCENTAGE')
    else:  # Landsat
        filtered = collection.filterBounds(point) \
                             .filterDate(start_date, end_date) \
                             .filter(ee.Filter.lt('CLOUD_COVER', 20)) \
                             .sort('CLOUD_COVER')

    image = filtered.first()
    if not image:
        st.warning(f"No {name} images found matching the criteria!")
        return None

    if 'LANDSAT' in name:
        image = image.select(['SR_B4', 'SR_B3', 'SR_B2']).multiply(0.0000275).add(-0.2)
    elif 'SENTINEL' in name:
        image = image.select(['B4', 'B3', 'B2']).divide(10000)

    return image.clip(region)

# Function to save images locally
def save_images_locally(image, name, region, lat, lon, output_dir):
    if not image:
        return None

    os.makedirs(output_dir, exist_ok=True)
    base_filename = f"{output_dir}/{name}_{lat:.4f}_{lon:.4f}"

    # Save GeoTIFF
    geemap.ee_export_image(
        image,
        filename=f'{base_filename}.tif',
        scale=10,
        region=region,
        file_per_band=False
    )

    # Visualization parameters
    vis_params = {
        'bands': ['SR_B4', 'SR_B3', 'SR_B2'] if 'LANDSAT' in name.upper() else ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 3000,
        'gamma': 1.4
    }

    # Visualize RGB image
    rgb_image = image.visualize(**vis_params)
    rgb_tif_path = f'{base_filename}_rgb.tif'
    geemap.ee_export_image(
        rgb_image,
        filename=rgb_tif_path,
        scale=10,
        region=region
    )

    # Convert RGB TIF to PNG
    png_path = f'{base_filename}.png'
    with Image.open(rgb_tif_path) as img:
        img.convert('RGB').save(png_path, 'PNG')

    return png_path

# Streamlit interface
st.title("Satellite Image Viewer and Downloader")

# Input fields for coordinates and date range
st.sidebar.header("Input Parameters")
lat = st.sidebar.number_input("Latitude", value=12.9716, format="%.6f")
lon = st.sidebar.number_input("Longitude", value=77.5946, format="%.6f")
start_date = st.sidebar.date_input("Start Date", value=datetime(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime(2023, 12, 31))

if st.sidebar.button("Process Images"):
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(225).bounds()

    # Get image collections
    landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

    # Process collections
    st.write("Processing satellite collections...")
    l8_image = process_collection(landsat8, "LANDSAT_8", point, region, str(start_date), str(end_date))
    l9_image = process_collection(landsat9, "LANDSAT_9", point, region, str(start_date), str(end_date))
    s2_image = process_collection(sentinel2, "SENTINEL_2", point, region, str(start_date), str(end_date))

    # Save images locally
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"satellite_images_{timestamp}"
    l8_path = save_images_locally(l8_image, "LANDSAT_8", region, lat, lon, output_dir)
    l9_path = save_images_locally(l9_image, "LANDSAT_9", region, lat, lon, output_dir)
    s2_path = save_images_locally(s2_image, "SENTINEL_2", region, lat, lon, output_dir)

    st.success(f"Images saved to: {os.path.abspath(output_dir)}")

    # Display images
    if l8_path:
        st.image(l8_path, caption="Landsat 8 Image", use_column_width=True)
    if l9_path:
        st.image(l9_path, caption="Landsat 9 Image", use_column_width=True)
    if s2_path:
        st.image(s2_path, caption="Sentinel-2 Image", use_column_width=True)