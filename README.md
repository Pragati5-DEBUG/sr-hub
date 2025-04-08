# SR Hub - Super Resolution Image Comparison Dashboard

A streamlit-based web application for comparing and analyzing original images with their super-resolution counterparts. The application supports various image formats including PNG, JPG, JPEG, and TIFF files.

## Features

- Side-by-side comparison of original and super-resolution images
- Support for multiple image formats (PNG, JPG, JPEG, TIFF)
- Detailed image analysis metrics:
  - RGB channel comparison
  - Color distribution analysis
  - Channel-wise difference visualization
- Beautiful modern UI with a responsive design
- Support for high-bit-depth TIFF images

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sr-hub.git
cd sr-hub
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application using:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:8502`

## Features

1. **Image Upload**
   - Upload original low-resolution images
   - Upload super-resolution results
   - Supports various image formats

2. **Image Analysis**
   - Resolution comparison
   - Color mode information
   - File format details

3. **Analysis Metrics**
   - RGB channel analysis
   - Color distribution visualization
   - Channel-wise comparison

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 