# Image Analysis GUI

A Python-based GUI application for image analysis and processing.

## Features

### Basic Operations
- **Brightness/Contrast Adjustment**: Fine-tune image brightness and contrast
- **Rotation**: Rotate images by any angle
- **Flip**: Horizontal and vertical flipping
- **Resize**: Scale images up or down

### Filters
- **Blur**: Gaussian, Average, and Median blur filters
- **Edge Detection**: Canny, Sobel, and Laplacian edge detection
- **Threshold**: Binary, Otsu, and Adaptive thresholding
- **Morphology**: Erosion, Dilation, Opening, and Closing operations

### Analysis
- **Histogram**: View and analyze color/grayscale histograms
- **Histogram Equalization**: Enhance image contrast
- **Color Space Conversion**: Convert between RGB, Grayscale, HSV, and LAB
- **Image Statistics**: View min, max, mean, and standard deviation

---

## Image Compare Tool

A dedicated tool for comparing two images side-by-side with pixel difference visualization.

### Features

| Feature | Description |
|---------|-------------|
| **Dual Image Loading** | Load two images independently for comparison |
| **Three-Panel View** | Left (Image 1), Center (Image 2), Right (Pixel Difference) |
| **Pixel Difference** | Visual heatmap showing differences (Red=high, Green=low) |
| **Synchronized Zoom** | All three panels zoom together |
| **Pan/Drag** | Click and drag to navigate images |
| **Center View** | Reset to image center with 100x100 pixel default view |
| **Fit to Window** | Auto-scale to fit entire image in view |

### Quick Start

```bash
# Run the Image Compare Tool
python src/image_compare_app.py
```

### Usage Examples

#### Example 1: Compare Calibrated vs Non-Calibrated Images

```bash
python src/image_compare_app.py
```

1. Click **"Load Image 1"** → Select `data/W32_cal.tif`
2. Click **"Load Image 2"** → Select `data/W32_nocal.tif`
3. View the pixel difference in the right panel
4. Use **mouse wheel** to zoom in/out on areas of interest
5. Click **"Center"** to reset view to center (100x100 pixels)

#### Example 2: Compare Test Pattern Images

```bash
# First, generate test images if not already created
python data/create_test_images.py

# Then run the compare tool
python src/image_compare_app.py
```

Test image pairs available:
- `test_image_A.png` vs `test_image_B.png` - Gradient with noise difference
- `test_circle_A.png` vs `test_circle_B.png` - Position offset detection
- `test_checker_A.png` vs `test_checker_B.png` - Brightness variation
- `test_color_A.png` vs `test_color_B.png` - Color channel inversion

#### Example 3: Analyzing Specific Regions

1. Load two images to compare
2. Click **"Fit to Window"** to see the full image
3. Use **mouse wheel** to zoom into a region of interest
4. **Click and drag** to pan around the image
5. Watch the **status bar** for pixel coordinates
6. Click **"Center"** to return to the 100x100 center view

### Controls Reference

| Control | Action |
|---------|--------|
| **Load Image 1** | Open file dialog to load first image |
| **Load Image 2** | Open file dialog to load second image |
| **+ / -** | Zoom in / out (10% steps) |
| **Mouse Wheel** | Zoom in / out |
| **Click + Drag** | Pan/navigate the image |
| **Center** | Reset to image center, 100x100 view, 100% zoom |
| **Fit to Window** | Scale image to fit canvas |

### Supported Image Formats

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- TIFF (`.tif`, `.tiff`) - including 16-bit images
- BMP (`.bmp`)
- GIF (`.gif`)

### Understanding the Difference View

The right panel shows pixel differences as a colored heatmap:

```
Red   (255, 0, 0)   = Maximum difference
Green (0, 255, 0)   = No difference
Yellow/Orange       = Partial difference
```

The difference is calculated as:
```python
diff = abs(image1_grayscale - image2_grayscale)
normalized_diff = diff / max(diff) * 255
```

---

## Installation

1. Clone or download this project
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies

```
numpy
Pillow
tkinter (included with Python)
```

## Usage

### Main Application
```bash
python main.py
```

### Image Compare Tool
```bash
python src/image_compare_app.py
```

### Generate Test Images
```bash
python data/create_test_images.py
```

## Project Structure

```
20260307_Image_Analysis_GUI/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── gui/
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── image_viewer.py         # Image display widget
│   └── control_panel.py        # Control panel with processing options
├── core/
│   ├── __init__.py
│   └── image_processor.py      # Image processing functions
├── src/
│   ├── __init__.py
│   └── image_compare_app.py    # Image Compare Tool (standalone)
├── data/
│   ├── create_test_images.py   # Script to generate test images
│   ├── test_image_A.png        # Test gradient image
│   ├── test_image_B.png        # Test gradient + noise
│   ├── test_circle_A.png       # Test circle pattern
│   ├── test_circle_B.png       # Test circle with offset
│   ├── test_checker_A.png      # Test checkerboard
│   ├── test_checker_B.png      # Test checkerboard brighter
│   ├── test_color_A.png        # Test RGB gradient
│   ├── test_color_B.png        # Test RGB inverted
│   └── *.tif                   # Sample TIFF images
└── utils/
    ├── __init__.py
    └── helpers.py              # Utility functions
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O   | Open Image |
| Ctrl+S   | Save Image |
| Ctrl+Q   | Exit Application |
| Mouse Wheel | Zoom In/Out |

## Troubleshooting

### Images appear black or white
- 16-bit TIFF images are automatically normalized to 8-bit for display
- Check if the image file is corrupted

### Size mismatch warning
- When comparing images of different sizes, the tool uses the smaller dimensions
- Consider resizing images to match before comparison

### Zoom not working
- Click on one of the image panels first to ensure focus
- Use the +/- buttons as an alternative

## Author

Created by: Byung Geun (BG) Jun
Date: 2026-03-07
