"""
Helper functions for Image Analysis GUI.
"""

import os
import numpy as np
from typing import Tuple, Optional


def get_image_info(image: np.ndarray) -> dict:
    """Get detailed information about an image.

    Args:
        image: Image as numpy array.

    Returns:
        Dictionary containing image information.
    """
    info = {
        "width": image.shape[1],
        "height": image.shape[0],
        "channels": 1 if len(image.shape) == 2 else image.shape[2],
        "dtype": str(image.dtype),
        "size_bytes": image.nbytes,
        "size_mb": round(image.nbytes / (1024 * 1024), 2),
    }
    return info


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to 0-255 range.

    Args:
        image: Input image.

    Returns:
        Normalized image as uint8.
    """
    if image.dtype == np.uint8:
        return image

    min_val = np.min(image)
    max_val = np.max(image)

    if max_val - min_val == 0:
        return np.zeros_like(image, dtype=np.uint8)

    normalized = ((image - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    return normalized


def validate_image_path(file_path: str) -> Tuple[bool, str]:
    """Validate if the file path is a valid image.

    Args:
        file_path: Path to the file.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"

    if not os.path.isfile(file_path):
        return False, "Path is not a file"

    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif'}
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in valid_extensions:
        return False, f"Unsupported file extension: {ext}"

    return True, ""


def create_thumbnail(image: np.ndarray, max_size: int = 256) -> np.ndarray:
    """Create a thumbnail of the image.

    Args:
        image: Input image.
        max_size: Maximum dimension of the thumbnail.

    Returns:
        Thumbnail image.
    """
    import cv2

    height, width = image.shape[:2]

    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)

    thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return thumbnail
