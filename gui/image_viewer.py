"""
Image Viewer Widget for displaying and interacting with images.
"""

import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


class ImageViewer(QWidget):
    """Widget for displaying images with zoom and pan capabilities."""

    zoom_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.current_pixmap = None
        self.zoom_factor = 1.0
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(False)
        self.image_label.setText("No image loaded\n\nDrag and drop an image or use File > Open")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #888888;
                font-size: 14px;
                border: 2px dashed #555555;
                border-radius: 10px;
            }
        """)

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def set_image(self, image):
        """Set the image to display.

        Args:
            image: numpy array (BGR or grayscale)
        """
        if image is None:
            return

        # Convert numpy array to QPixmap
        if len(image.shape) == 2:
            # Grayscale
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(
                image.data, width, height, bytes_per_line, QImage.Format_Grayscale8
            )
        else:
            # Color (BGR to RGB)
            height, width, channels = image.shape
            if channels == 3:
                import cv2
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * width
                q_image = QImage(
                    rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888
                )
            elif channels == 4:
                import cv2
                rgba_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
                bytes_per_line = 4 * width
                q_image = QImage(
                    rgba_image.data, width, height, bytes_per_line, QImage.Format_RGBA8888
                )
            else:
                return

        self.current_pixmap = QPixmap.fromImage(q_image)
        self._update_display()

        # Reset style for image display
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
            }
        """)

    def _update_display(self):
        """Update the displayed image with current zoom factor."""
        if self.current_pixmap is None:
            return

        scaled_pixmap = self.current_pixmap.scaled(
            self.current_pixmap.size() * self.zoom_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.adjustSize()

    def zoom_in(self):
        """Zoom in by 25%."""
        self.zoom_factor *= 1.25
        self._update_display()
        self.zoom_changed.emit(self.zoom_factor)

    def zoom_out(self):
        """Zoom out by 25%."""
        self.zoom_factor *= 0.8
        self._update_display()
        self.zoom_changed.emit(self.zoom_factor)

    def zoom_reset(self):
        """Reset zoom to 100%."""
        self.zoom_factor = 1.0
        self._update_display()
        self.zoom_changed.emit(self.zoom_factor)

    def fit_to_window(self):
        """Fit the image to the window size."""
        if self.current_pixmap is None:
            return

        available_size = self.scroll_area.size()
        pixmap_size = self.current_pixmap.size()

        scale_w = available_size.width() / pixmap_size.width()
        scale_h = available_size.height() / pixmap_size.height()
        self.zoom_factor = min(scale_w, scale_h) * 0.95

        self._update_display()
        self.zoom_changed.emit(self.zoom_factor)

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            # Emit signal or call parent method to load image
            parent = self.window()
            if hasattr(parent, 'image_processor'):
                image = parent.image_processor.load_image(file_path)
                if image is not None:
                    parent.current_image = image
                    self.set_image(image)
