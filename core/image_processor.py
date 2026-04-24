"""
Image Processor - Core image processing operations.
"""

import cv2
import numpy as np
import os
from typing import Optional, Dict, Any, Tuple


class ImageProcessor:
    """Class for image processing operations."""

    def __init__(self):
        """Initialize the image processor."""
        pass

    def load_image(self, file_path: str) -> Optional[np.ndarray]:
        """Load an image or CSV file.

        Args:
            file_path: Path to the image or CSV file.

        Returns:
            Image as numpy array or None if failed.
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.csv':
                return self._load_csv_as_image(file_path)

            image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            return image
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def _load_csv_as_image(self, file_path: str) -> Optional[np.ndarray]:
        """Load CSV file as a grayscale image (numpy array).

        Supports comma, tab, semicolon, or space delimited files.
        Automatically skips header rows with non-numeric data.

        Returns:
            Grayscale image as numpy array (uint8) or None if failed.
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                sample = f.read(4096)

            delimiter = ','
            for delim in [',', '\t', ';', ' ']:
                lines = sample.strip().split('\n')
                if len(lines) > 0 and len(lines[0].split(delim)) > 1:
                    delimiter = delim
                    break

            skip_rows = 0
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        skip_rows += 1
                        continue
                    parts = line.split(delimiter)
                    try:
                        [float(p.strip()) for p in parts if p.strip()]
                        break
                    except ValueError:
                        skip_rows += 1

            arr = np.loadtxt(file_path, delimiter=delimiter, skiprows=skip_rows)
            if arr.ndim == 1:
                arr = arr.reshape(1, -1)

            arr_min, arr_max = arr.min(), arr.max()
            if arr_max - arr_min > 0:
                arr = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)
            else:
                arr = np.zeros_like(arr, dtype=np.uint8)

            return arr
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None

    def save_image(self, image: np.ndarray, file_path: str) -> bool:
        """Save an image to file.

        Args:
            image: Image as numpy array.
            file_path: Path to save the image.

        Returns:
            True if successful, False otherwise.
        """
        try:
            cv2.imwrite(file_path, image)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def process(self, image: np.ndarray, operation: str, params: Dict[str, Any]) -> Optional[np.ndarray]:
        """Process an image with the specified operation.

        Args:
            image: Input image as numpy array.
            operation: Name of the operation to perform.
            params: Parameters for the operation.

        Returns:
            Processed image or None if failed.
        """
        operations = {
            "brightness_contrast": self._brightness_contrast,
            "rotate": self._rotate,
            "flip": self._flip,
            "resize": self._resize,
            "blur": self._blur,
            "edge": self._edge_detection,
            "threshold": self._threshold,
            "morphology": self._morphology,
            "color_convert": self._color_convert,
            "equalize": self._histogram_equalization,
        }

        if operation in operations:
            return operations[operation](image, params)
        else:
            print(f"Unknown operation: {operation}")
            return None

    def _brightness_contrast(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Adjust brightness and contrast."""
        brightness = params.get("brightness", 0)
        contrast = params.get("contrast", 0)

        # Convert contrast from -100~100 to 0~3
        alpha = 1.0 + (contrast / 100.0)
        beta = brightness

        result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return result

    def _rotate(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Rotate the image."""
        angle = params.get("angle", 0)

        height, width = image.shape[:2]
        center = (width // 2, height // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Calculate new bounding box
        abs_cos = abs(rotation_matrix[0, 0])
        abs_sin = abs(rotation_matrix[0, 1])
        new_width = int(height * abs_sin + width * abs_cos)
        new_height = int(height * abs_cos + width * abs_sin)

        rotation_matrix[0, 2] += (new_width - width) / 2
        rotation_matrix[1, 2] += (new_height - height) / 2

        result = cv2.warpAffine(image, rotation_matrix, (new_width, new_height))
        return result

    def _flip(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Flip the image."""
        direction = params.get("direction", "horizontal")

        if direction == "horizontal":
            return cv2.flip(image, 1)
        else:
            return cv2.flip(image, 0)

    def _resize(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Resize the image."""
        scale = params.get("scale", 1.0)

        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)

        result = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
        return result

    def _blur(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Apply blur filter."""
        kernel = params.get("kernel", 5)
        blur_type = params.get("type", "gaussian")

        if blur_type == "gaussian":
            return cv2.GaussianBlur(image, (kernel, kernel), 0)
        elif blur_type == "average":
            return cv2.blur(image, (kernel, kernel))
        elif blur_type == "median":
            return cv2.medianBlur(image, kernel)
        else:
            return image

    def _edge_detection(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Apply edge detection."""
        edge_type = params.get("type", "canny")

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        if edge_type == "canny":
            return cv2.Canny(gray, 100, 200)
        elif edge_type == "sobel":
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            return cv2.magnitude(sobel_x, sobel_y).astype(np.uint8)
        elif edge_type == "laplacian":
            return cv2.Laplacian(gray, cv2.CV_64F).astype(np.uint8)
        else:
            return gray

    def _threshold(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Apply threshold."""
        value = params.get("value", 127)
        thresh_type = params.get("type", "binary")

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        if thresh_type == "binary":
            _, result = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        elif thresh_type == "binary inv":
            _, result = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY_INV)
        elif thresh_type == "otsu":
            _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif thresh_type == "adaptive":
            result = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        else:
            result = gray

        return result

    def _morphology(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Apply morphological operation."""
        morph_type = params.get("type", "erosion")
        kernel_size = params.get("kernel", 3)

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        if morph_type == "erosion":
            return cv2.erode(image, kernel, iterations=1)
        elif morph_type == "dilation":
            return cv2.dilate(image, kernel, iterations=1)
        elif morph_type == "opening":
            return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        elif morph_type == "closing":
            return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        else:
            return image

    def _color_convert(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Convert color space."""
        space = params.get("space", "grayscale")

        if len(image.shape) == 2:
            # Already grayscale
            if space == "grayscale":
                return image
            else:
                # Convert grayscale to BGR first
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        if space == "grayscale":
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif space == "hsv":
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif space == "lab":
            return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        elif space == "rgb":
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            return image

    def _histogram_equalization(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """Apply histogram equalization."""
        if len(image.shape) == 2:
            return cv2.equalizeHist(image)
        else:
            # Convert to YUV and equalize Y channel
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    def show_histogram(self, image: np.ndarray):
        """Display histogram of the image."""
        import matplotlib.pyplot as plt

        if len(image.shape) == 2:
            plt.figure(figsize=(10, 4))
            plt.hist(image.ravel(), 256, [0, 256], color='gray')
            plt.title("Grayscale Histogram")
            plt.xlabel("Pixel Value")
            plt.ylabel("Frequency")
        else:
            colors = ('b', 'g', 'r')
            plt.figure(figsize=(10, 4))
            for i, color in enumerate(colors):
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                plt.plot(hist, color=color)
            plt.title("Color Histogram")
            plt.xlabel("Pixel Value")
            plt.ylabel("Frequency")
            plt.legend(['Blue', 'Green', 'Red'])

        plt.tight_layout()
        plt.show()

    def get_statistics(self, image: np.ndarray) -> Dict[str, Any]:
        """Get statistics of the image."""
        stats = {
            "shape": image.shape,
            "dtype": str(image.dtype),
            "min": int(np.min(image)),
            "max": int(np.max(image)),
            "mean": round(float(np.mean(image)), 2),
            "std": round(float(np.std(image)), 2),
        }
        return stats
