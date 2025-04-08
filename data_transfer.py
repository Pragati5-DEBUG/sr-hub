
import ee
import folium
import geemap
import os
import webbrowser
from IPython.display import Image, display
from datetime import datetime
from PIL import Image

# 2. AUTHENTICATION & INITIALIZATION
# ----------------------------------
def authenticate_and_initialize():
    """Handles GEE authentication and initialization"""
    try:
        # Try to initialize (if already authenticated)
        ee.Initialize()
        print("Earth Engine initialized successfully!")
    except Exception as e:
        print("Authentication needed. Please follow these steps:")
        print("1. A browser window will open")
        print("2. Sign in with your Google account")
        print("3. Copy the authorization code")
        
        # Force authentication
        ee.Authenticate(auth_mode="notebook")
        
        # Initialize after authentication
        ee.Initialize()
        print("\nEarth Engine initialized successfully!")

# Run authentication
authenticate_and_initialize()

def get_user_input():
    """Gets user input for coordinates and date range"""
    print("\n=== SATELLITE IMAGE DOWNLOAD TOOL ===")
    while True:
        try:
            lat = float(input("Enter latitude (e.g., 12.9716 for Bangalore): "))

            lon = float(input("Enter longitude (e.g., 77.5946 for Bangalore): "))
            break
        except ValueError:
            print("Invalid coordinates! Please enter numeric values.")
        
    print("\nEnter date range (YYYY-MM-DD format):")
    while True:
        try:
            start_date = input("Start date (e.g., 2023-01-01): ")
            end_date = input("End date (e.g., 2023-12-31): ")
            # Validate dates
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            if end_date < start_date:
                print("Error: End date must be after start date.")
                continue
                
            break
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD.")
    
    return lat, lon, start_date, end_date
get_user_input()

def get_image_collections():
    """Returns all three image collections"""
    landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    sentinel2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    return landsat8, landsat9, sentinel2
get_image_collections()

def process_collection(collection, name, point, region, start_date, end_date):
    """Processes an individual collection"""
    # Different filtering for Sentinel vs Landsat
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
    
    # Get the least cloudy image
    image = filtered.first()
    
    if not image:
        print(f"\nNo {name} images found matching the criteria!")
        return None
    
    # Process bands
    if 'LANDSAT' in name:
        image = image.select(['SR_B4', 'SR_B3', 'SR_B2']).multiply(0.0000275).add(-0.2)
    elif 'SENTINEL' in name:
        image = image.select(['B4', 'B3', 'B2']).divide(10000)
    
    return image.clip(region)


import geemap
import ee
import os
from PIL import Image

def save_images_locally(image, name, region, lat, lon, output_dir):
    if not image:
        print(" No image found.")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    base_filename = f"{output_dir}/{name}_{lat:.4f}_{lon:.4f}"

    # Save GeoTIFF
    print(f" Saving {name} GeoTIFF...")
    geemap.ee_export_image(
        image,
        filename=f'{base_filename}.tif',
        scale=10,
        region=region,
        file_per_band=False
    )

    # Visualization parameters
    print(f" Creating {name} RGB visualization...")
    if 'LANDSAT' in name.upper():
        vis_params = {
            'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
            'min': 0,
            'max': 3000,
            'gamma': 1.4
        }
    else:  # Sentinel
        vis_params = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 3000,
            'gamma': 1.4
        }

    # Visualize RGB image
    rgb_image = image.visualize(**vis_params)

    # Save as temporary RGB TIF
    rgb_tif_path = f'{base_filename}_rgb.tif'
    print(f" Exporting RGB TIF for {name}...")
    geemap.ee_export_image(
        rgb_image,
        filename=rgb_tif_path,
        scale=10,
        region=region
    )

    # Convert RGB TIF to PNG
    png_path = f'{base_filename}.png'
    print(f" Converting to PNG: {png_path}")
    try:
        with Image.open(rgb_tif_path) as img:
            img.convert('RGB').save(png_path, 'PNG')
        print(" PNG saved successfully!")
    except Exception as e:
        print(" Error converting to PNG:", e)

def main_processing():
    lat, lon, start_date, end_date = get_user_input()
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(225).bounds()
    
    landsat8, landsat9, sentinel2 = get_image_collections()
    
    print("\nProcessing satellite collections...")
    l8_image = process_collection(landsat8, "LANDSAT_8", point, region, start_date, end_date)
    l9_image = process_collection(landsat9, "LANDSAT_9", point, region, start_date, end_date)
    s2_image = process_collection(sentinel2, "SENTINEL_2", point, region, start_date, end_date)
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"satellite_images_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save all available images
    save_images_locally(l8_image, "LANDSAT_8", region, lat, lon, output_dir)
    save_images_locally(l9_image, "LANDSAT_9", region, lat, lon, output_dir)
    save_images_locally(s2_image, "SENTINEL_2", region, lat, lon, output_dir)
    
    print("\n=== PROCESSING COMPLETE ===")
    print(f"All images saved to: {os.path.abspath(output_dir)}")
# 6. RUN THE MAIN PROCESSING
# --------------------------
if __name__ == '__main__':
    main_processing()