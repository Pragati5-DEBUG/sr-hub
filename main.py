import streamlit as st
import numpy as np
from PIL import Image
import io
import os
import base64
import tifffile

# Set page configuration
st.set_page_config(
    page_title="SR Hub - Image Comparison",
    page_icon="🔍",
    layout="wide"
)

# Function to encode video to base64
def get_base64_video(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode()

# Copy video to current directory if it doesn't exist
video_path = "background.mp4"
if not os.path.exists(video_path):
    import shutil
    original_video = r"C:\Users\user\Downloads\istockphoto-2160507892-640_adpp_is.mp4"
    shutil.copy2(original_video, video_path)

# Get base64 encoded video
video_base64 = get_base64_video(video_path)

# Add custom CSS and HTML for video background
background_style = f"""
    <style>
    .stApp {{
        background: transparent;
    }}
    
    .video-background {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -1;
        object-fit: cover;
    }}

    .content-overlay {{
        position: relative;
        z-index: 1;
    }}

    .file-limitation-text {{
        font-size: 0.8em;
        color: rgba(255, 255, 255, 0.7);
    }}
    </style>

    <video autoplay muted loop playsinline class="video-background">
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>

    <div class="content-overlay">
"""

# Add custom CSS for styling
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

.main {
    background: none !important;
}

.css-1d391kg, .css-12oz5g7 {
    background-color: rgba(13, 27, 52, 0.4) !important;
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.stButton>button {
    background-color: rgba(51, 99, 255, 0.4);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 10px 15px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: rgba(51, 99, 255, 0.6);
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 0 15px rgba(51, 99, 255, 0.4);
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    background: linear-gradient(120deg, #00ffff, #7f00ff) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
    letter-spacing: 1px !important;
}

.metric-card {
    background-color: rgba(13, 27, 52, 0.4);
    border-radius: 10px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.logo-text {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 3em !important;
    font-weight: bold !important;
    background: linear-gradient(45deg, #00ffff, #7f00ff) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-shadow: none !important;
    letter-spacing: 2px !important;
}

/* Style for the file uploader */
.uploadedFile {
    background-color: rgba(13, 27, 52, 0.4) !important;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
}

/* Style for select boxes */
.stSelectbox > div > div {
    background-color: rgba(13, 27, 52, 0.4);
    border-color: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
}
</style>
"""

# Close the content-overlay div at the end of your content
end_div = """
    </div>
"""

# Apply styles
st.markdown(background_style, unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)

# Title with SR Hub branding
st.markdown('<h1 class="logo-text">SR Hub</h1>', unsafe_allow_html=True)
st.markdown("### Super Resolution Image Comparison Dashboard")

# Create two columns for image upload
col1, col2 = st.columns(2)

def normalize_array(arr):
    """Normalize array to 0-255 range and convert to uint8"""
    if arr.dtype == np.float64 or arr.dtype == np.float32:
        # Normalize float arrays to 0-255 range
        arr_min = arr.min()
        arr_max = arr.max()
        if arr_max != arr_min:
            arr = ((arr - arr_min) * 255 / (arr_max - arr_min))
        else:
            arr = arr - arr_min
        arr = arr.astype(np.uint8)
    return arr

with col1:
    st.header("Original Image")
    image1 = st.file_uploader("Upload original low-resolution image", type=['png', 'jpg', 'jpeg', 'tif', 'tiff'], key="img1")
    st.markdown('<p class="file-limitation-text">Limit 200MB per file • PNG, JPG, JPEG, TIF, TIFF</p>', unsafe_allow_html=True)
    if image1 is not None:
        try:
            # Check if it's a TIFF file
            if image1.type == 'image/tiff':
                # Read TIFF file
                tiff_bytes = image1.read()
                img1_array = tifffile.imread(io.BytesIO(tiff_bytes))
                # Normalize and convert the array
                img1_array = normalize_array(img1_array)
                # Convert to PIL Image
                if img1_array.ndim == 2:  # If grayscale
                    img1 = Image.fromarray(img1_array, mode='L')
                elif img1_array.ndim == 3:  # If RGB/RGBA
                    if img1_array.shape[2] > 3:  # If more than 3 channels
                        img1_array = img1_array[:,:,:3]  # Take only RGB channels
                    img1 = Image.fromarray(img1_array, mode='RGB')
            else:
                img1 = Image.open(image1)
            
            st.image(img1, use_container_width=True)
            # Image details
            st.markdown("### Original Image Details")
            st.write(f"Resolution: {img1.size[0]} × {img1.size[1]} pixels")
            st.write(f"Color Mode: {img1.mode}")
            st.write(f"File Format: {image1.type}")
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            img1 = None

with col2:
    st.header("Super Resolution Result")
    image2 = st.file_uploader("Upload super resolution result", type=['png', 'jpg', 'jpeg', 'tif', 'tiff'], key="img2")
    st.markdown('<p class="file-limitation-text">Limit 200MB per file • PNG, JPG, JPEG, TIF, TIFF</p>', unsafe_allow_html=True)
    if image2 is not None:
        try:
            # Check if it's a TIFF file
            if image2.type == 'image/tiff':
                # Read TIFF file
                tiff_bytes = image2.read()
                img2_array = tifffile.imread(io.BytesIO(tiff_bytes))
                # Normalize and convert the array
                img2_array = normalize_array(img2_array)
                # Convert to PIL Image
                if img2_array.ndim == 2:  # If grayscale
                    img2 = Image.fromarray(img2_array, mode='L')
                elif img2_array.ndim == 3:  # If RGB/RGBA
                    if img2_array.shape[2] > 3:  # If more than 3 channels
                        img2_array = img2_array[:,:,:3]  # Take only RGB channels
                    img2 = Image.fromarray(img2_array, mode='RGB')
            else:
                img2 = Image.open(image2)
            
            st.image(img2, use_container_width=True)
            # Image details
            st.markdown("### SR Image Details")
            st.write(f"Resolution: {img2.size[0]} × {img2.size[1]} pixels")
            st.write(f"Color Mode: {img2.mode}")
            st.write(f"File Format: {image2.type}")
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            img2 = None

# Comparison metrics
st.markdown("---")
st.header("SR Analysis Metrics")

if image1 is not None and image2 is not None:
    # Create three columns for RGB metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    # Convert images to RGB arrays
    img1_array = np.array(img1.convert('RGB'))
    img2_array = np.array(img2.convert('RGB'))
    
    # Calculate average RGB values
    avg_rgb1 = np.mean(img1_array, axis=(0,1))
    avg_rgb2 = np.mean(img2_array, axis=(0,1))
    
    with metric_col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Red Channel",
            value=f"{avg_rgb2[0]:.1f}",
            delta=f"{avg_rgb2[0] - avg_rgb1[0]:.1f} from original"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with metric_col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Green Channel",
            value=f"{avg_rgb2[1]:.1f}",
            delta=f"{avg_rgb2[1] - avg_rgb1[1]:.1f} from original"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with metric_col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Blue Channel",
            value=f"{avg_rgb2[2]:.1f}",
            delta=f"{avg_rgb2[2] - avg_rgb1[2]:.1f} from original"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Additional analysis options
    st.markdown("### Detailed Analysis")
    analysis_type = st.selectbox(
        "Choose analysis type",
        ["RGB Distribution", "Color Histogram", "Channel Comparison"]
    )

    if analysis_type == "RGB Distribution":
        # Show RGB distribution
        st.write("RGB Value Distribution")
        
        # Create columns for each image
        dist_col1, dist_col2 = st.columns(2)
        
        with dist_col1:
            st.write("Original Image RGB Distribution")
            for channel, color in [('Red', 'red'), ('Green', 'green'), ('Blue', 'blue')]:
                channel_idx = 0 if channel=='Red' else 1 if channel=='Green' else 2
                st.write(f"{channel} Channel")
                st.bar_chart(np.histogram(img1_array[:,:,channel_idx], bins=50)[0])
        
        with dist_col2:
            st.write("SR Result RGB Distribution")
            for channel, color in [('Red', 'red'), ('Green', 'green'), ('Blue', 'blue')]:
                channel_idx = 0 if channel=='Red' else 1 if channel=='Green' else 2
                st.write(f"{channel} Channel")
                st.bar_chart(np.histogram(img2_array[:,:,channel_idx], bins=50)[0])

    elif analysis_type == "Color Histogram":
        # Show color histograms
        hist_col1, hist_col2 = st.columns(2)
        with hist_col1:
            st.write("Original Image RGB Histogram")
            for channel, color in [('Red', 'red'), ('Green', 'green'), ('Blue', 'blue')]:
                st.bar_chart(np.histogram(img1_array[:,:,0 if channel=='Red' else 1 if channel=='Green' else 2], bins=50)[0])
        
        with hist_col2:
            st.write("SR Result RGB Histogram")
            for channel, color in [('Red', 'red'), ('Green', 'green'), ('Blue', 'blue')]:
                st.bar_chart(np.histogram(img2_array[:,:,0 if channel=='Red' else 1 if channel=='Green' else 2], bins=50)[0])

    elif analysis_type == "Channel Comparison":
        # Show channel-wise comparison
        st.write("Channel-wise Comparison")
        for channel, color in [('Red', 'red'), ('Green', 'green'), ('Blue', 'blue')]:
            channel_idx = 0 if channel=='Red' else 1 if channel=='Green' else 2
            diff = np.abs(img2_array[:,:,channel_idx] - img1_array[:,:,channel_idx])
            st.write(f"{channel} Channel Difference")
            st.bar_chart(np.histogram(diff, bins=50)[0])

else:
    st.info("Please upload both the original image and its super resolution result to see RGB analysis metrics")

# Close the content-overlay div
st.markdown(end_div, unsafe_allow_html=True) 