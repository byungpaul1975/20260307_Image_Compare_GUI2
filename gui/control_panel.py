"""
Control Panel Widget for image processing operations.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QTabWidget, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal


class ControlPanel(QWidget):
    """Control panel for image processing operations."""

    process_requested = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Create tab widget for different categories
        self.tab_widget = QTabWidget()

        # Basic operations tab
        basic_tab = self._create_basic_tab()
        self.tab_widget.addTab(basic_tab, "Basic")

        # Filters tab
        filters_tab = self._create_filters_tab()
        self.tab_widget.addTab(filters_tab, "Filters")

        # Analysis tab
        analysis_tab = self._create_analysis_tab()
        self.tab_widget.addTab(analysis_tab, "Analysis")

        layout.addWidget(self.tab_widget)

    def _create_basic_tab(self):
        """Create basic operations tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Brightness/Contrast group
        bc_group = QGroupBox("Brightness / Contrast")
        bc_layout = QVBoxLayout(bc_group)

        # Brightness slider
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_value = QLabel("0")
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        bc_layout.addLayout(brightness_layout)

        self.brightness_slider.valueChanged.connect(
            lambda v: self.brightness_value.setText(str(v))
        )

        # Contrast slider
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("Contrast:"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_value = QLabel("0")
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_value)
        bc_layout.addLayout(contrast_layout)

        self.contrast_slider.valueChanged.connect(
            lambda v: self.contrast_value.setText(str(v))
        )

        # Apply button
        apply_bc_btn = QPushButton("Apply")
        apply_bc_btn.clicked.connect(self._apply_brightness_contrast)
        bc_layout.addWidget(apply_bc_btn)

        layout.addWidget(bc_group)

        # Transform group
        transform_group = QGroupBox("Transform")
        transform_layout = QVBoxLayout(transform_group)

        # Rotation
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotate:"))
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(-180, 180)
        self.rotation_spin.setValue(0)
        self.rotation_spin.setSuffix("°")
        rotation_layout.addWidget(self.rotation_spin)
        rotate_btn = QPushButton("Apply")
        rotate_btn.clicked.connect(self._apply_rotation)
        rotation_layout.addWidget(rotate_btn)
        transform_layout.addLayout(rotation_layout)

        # Flip buttons
        flip_layout = QHBoxLayout()
        flip_h_btn = QPushButton("Flip Horizontal")
        flip_h_btn.clicked.connect(lambda: self._apply_flip("horizontal"))
        flip_v_btn = QPushButton("Flip Vertical")
        flip_v_btn.clicked.connect(lambda: self._apply_flip("vertical"))
        flip_layout.addWidget(flip_h_btn)
        flip_layout.addWidget(flip_v_btn)
        transform_layout.addLayout(flip_layout)

        layout.addWidget(transform_group)

        # Resize group
        resize_group = QGroupBox("Resize")
        resize_layout = QVBoxLayout(resize_group)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Scale:"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 10.0)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setSingleStep(0.1)
        size_layout.addWidget(self.scale_spin)

        resize_btn = QPushButton("Apply")
        resize_btn.clicked.connect(self._apply_resize)
        size_layout.addWidget(resize_btn)
        resize_layout.addLayout(size_layout)

        layout.addWidget(resize_group)

        layout.addStretch()
        return widget

    def _create_filters_tab(self):
        """Create filters tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Blur group
        blur_group = QGroupBox("Blur")
        blur_layout = QVBoxLayout(blur_group)

        kernel_layout = QHBoxLayout()
        kernel_layout.addWidget(QLabel("Kernel Size:"))
        self.blur_kernel = QSpinBox()
        self.blur_kernel.setRange(1, 31)
        self.blur_kernel.setValue(5)
        self.blur_kernel.setSingleStep(2)
        kernel_layout.addWidget(self.blur_kernel)
        blur_layout.addLayout(kernel_layout)

        blur_type_layout = QHBoxLayout()
        blur_type_layout.addWidget(QLabel("Type:"))
        self.blur_type = QComboBox()
        self.blur_type.addItems(["Gaussian", "Average", "Median"])
        blur_type_layout.addWidget(self.blur_type)
        blur_layout.addLayout(blur_type_layout)

        blur_btn = QPushButton("Apply Blur")
        blur_btn.clicked.connect(self._apply_blur)
        blur_layout.addWidget(blur_btn)

        layout.addWidget(blur_group)

        # Edge Detection group
        edge_group = QGroupBox("Edge Detection")
        edge_layout = QVBoxLayout(edge_group)

        self.edge_type = QComboBox()
        self.edge_type.addItems(["Canny", "Sobel", "Laplacian"])
        edge_layout.addWidget(self.edge_type)

        edge_btn = QPushButton("Detect Edges")
        edge_btn.clicked.connect(self._apply_edge_detection)
        edge_layout.addWidget(edge_btn)

        layout.addWidget(edge_group)

        # Threshold group
        threshold_group = QGroupBox("Threshold")
        threshold_layout = QVBoxLayout(threshold_group)

        thresh_val_layout = QHBoxLayout()
        thresh_val_layout.addWidget(QLabel("Value:"))
        self.threshold_value = QSlider(Qt.Horizontal)
        self.threshold_value.setRange(0, 255)
        self.threshold_value.setValue(127)
        self.threshold_label = QLabel("127")
        thresh_val_layout.addWidget(self.threshold_value)
        thresh_val_layout.addWidget(self.threshold_label)
        threshold_layout.addLayout(thresh_val_layout)

        self.threshold_value.valueChanged.connect(
            lambda v: self.threshold_label.setText(str(v))
        )

        self.threshold_type = QComboBox()
        self.threshold_type.addItems(["Binary", "Binary Inv", "Otsu", "Adaptive"])
        threshold_layout.addWidget(self.threshold_type)

        thresh_btn = QPushButton("Apply Threshold")
        thresh_btn.clicked.connect(self._apply_threshold)
        threshold_layout.addWidget(thresh_btn)

        layout.addWidget(threshold_group)

        # Morphology group
        morph_group = QGroupBox("Morphology")
        morph_layout = QVBoxLayout(morph_group)

        self.morph_type = QComboBox()
        self.morph_type.addItems(["Erosion", "Dilation", "Opening", "Closing"])
        morph_layout.addWidget(self.morph_type)

        morph_kernel_layout = QHBoxLayout()
        morph_kernel_layout.addWidget(QLabel("Kernel:"))
        self.morph_kernel = QSpinBox()
        self.morph_kernel.setRange(1, 21)
        self.morph_kernel.setValue(3)
        self.morph_kernel.setSingleStep(2)
        morph_kernel_layout.addWidget(self.morph_kernel)
        morph_layout.addLayout(morph_kernel_layout)

        morph_btn = QPushButton("Apply")
        morph_btn.clicked.connect(self._apply_morphology)
        morph_layout.addWidget(morph_btn)

        layout.addWidget(morph_group)

        layout.addStretch()
        return widget

    def _create_analysis_tab(self):
        """Create analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Histogram group
        hist_group = QGroupBox("Histogram")
        hist_layout = QVBoxLayout(hist_group)

        show_hist_btn = QPushButton("Show Histogram")
        show_hist_btn.clicked.connect(lambda: self.process_requested.emit("histogram", {}))
        hist_layout.addWidget(show_hist_btn)

        equalize_btn = QPushButton("Histogram Equalization")
        equalize_btn.clicked.connect(lambda: self.process_requested.emit("equalize", {}))
        hist_layout.addWidget(equalize_btn)

        layout.addWidget(hist_group)

        # Color Space group
        color_group = QGroupBox("Color Space")
        color_layout = QVBoxLayout(color_group)

        self.color_space = QComboBox()
        self.color_space.addItems(["Grayscale", "HSV", "LAB", "RGB"])
        color_layout.addWidget(self.color_space)

        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self._apply_color_convert)
        color_layout.addWidget(convert_btn)

        layout.addWidget(color_group)

        # Measurements group
        measure_group = QGroupBox("Measurements")
        measure_layout = QVBoxLayout(measure_group)

        stats_btn = QPushButton("Image Statistics")
        stats_btn.clicked.connect(lambda: self.process_requested.emit("statistics", {}))
        measure_layout.addWidget(stats_btn)

        contours_btn = QPushButton("Find Contours")
        contours_btn.clicked.connect(lambda: self.process_requested.emit("contours", {}))
        measure_layout.addWidget(contours_btn)

        layout.addWidget(measure_group)

        layout.addStretch()
        return widget

    def _apply_brightness_contrast(self):
        """Apply brightness and contrast adjustments."""
        params = {
            "brightness": self.brightness_slider.value(),
            "contrast": self.contrast_slider.value()
        }
        self.process_requested.emit("brightness_contrast", params)

    def _apply_rotation(self):
        """Apply rotation."""
        params = {"angle": self.rotation_spin.value()}
        self.process_requested.emit("rotate", params)

    def _apply_flip(self, direction):
        """Apply flip transformation."""
        params = {"direction": direction}
        self.process_requested.emit("flip", params)

    def _apply_resize(self):
        """Apply resize."""
        params = {"scale": self.scale_spin.value()}
        self.process_requested.emit("resize", params)

    def _apply_blur(self):
        """Apply blur filter."""
        kernel = self.blur_kernel.value()
        if kernel % 2 == 0:
            kernel += 1
        params = {
            "kernel": kernel,
            "type": self.blur_type.currentText().lower()
        }
        self.process_requested.emit("blur", params)

    def _apply_edge_detection(self):
        """Apply edge detection."""
        params = {"type": self.edge_type.currentText().lower()}
        self.process_requested.emit("edge", params)

    def _apply_threshold(self):
        """Apply threshold."""
        params = {
            "value": self.threshold_value.value(),
            "type": self.threshold_type.currentText().lower()
        }
        self.process_requested.emit("threshold", params)

    def _apply_morphology(self):
        """Apply morphological operation."""
        kernel = self.morph_kernel.value()
        if kernel % 2 == 0:
            kernel += 1
        params = {
            "type": self.morph_type.currentText().lower(),
            "kernel": kernel
        }
        self.process_requested.emit("morphology", params)

    def _apply_color_convert(self):
        """Apply color space conversion."""
        params = {"space": self.color_space.currentText().lower()}
        self.process_requested.emit("color_convert", params)
