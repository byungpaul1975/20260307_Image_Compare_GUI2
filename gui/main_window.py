"""
Main Window for Image Analysis GUI
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QScrollArea,
    QStatusBar, QMenuBar, QMenu, QAction, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

from gui.image_viewer import ImageViewer
from gui.control_panel import ControlPanel
from core.image_processor import ImageProcessor


class MainWindow(QMainWindow):
    """Main window of the Image Analysis GUI application."""

    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.current_image = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Image Analysis GUI")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)

        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Image", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction("Save Image", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Analysis menu
        analysis_menu = menubar.addMenu("Analysis")

        histogram_action = QAction("Histogram", self)
        histogram_action.triggered.connect(self.show_histogram)
        analysis_menu.addAction(histogram_action)

        stats_action = QAction("Image Statistics", self)
        stats_action.triggered.connect(self.show_statistics)
        analysis_menu.addAction(stats_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Create the central widget with splitter layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Image viewer (left side)
        self.image_viewer = ImageViewer()
        splitter.addWidget(self.image_viewer)

        # Control panel (right side)
        self.control_panel = ControlPanel()
        self.control_panel.setMaximumWidth(350)
        self.control_panel.setMinimumWidth(250)
        splitter.addWidget(self.control_panel)

        # Set initial sizes (70% image viewer, 30% control panel)
        splitter.setSizes([840, 360])

        main_layout.addWidget(splitter)

        # Connect signals
        self.control_panel.process_requested.connect(self.process_image)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def open_image(self):
        """Open an image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "All supported files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.csv);;Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif);;CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.current_image = self.image_processor.load_image(file_path)
            if self.current_image is not None:
                self.image_viewer.set_image(self.current_image)
                self.status_bar.showMessage(f"Loaded: {file_path}")
            else:
                self.status_bar.showMessage("Failed to load image")

    def save_image(self):
        """Save the current image."""
        if self.current_image is None:
            self.status_bar.showMessage("No image to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )

        if file_path:
            success = self.image_processor.save_image(self.current_image, file_path)
            if success:
                self.status_bar.showMessage(f"Saved: {file_path}")
            else:
                self.status_bar.showMessage("Failed to save image")

    def process_image(self, operation, params):
        """Process the current image with the specified operation."""
        if self.current_image is None:
            self.status_bar.showMessage("No image loaded")
            return

        result = self.image_processor.process(self.current_image, operation, params)
        if result is not None:
            self.current_image = result
            self.image_viewer.set_image(self.current_image)
            self.status_bar.showMessage(f"Applied: {operation}")

    def show_histogram(self):
        """Show histogram of the current image."""
        if self.current_image is None:
            self.status_bar.showMessage("No image loaded")
            return
        self.image_processor.show_histogram(self.current_image)

    def show_statistics(self):
        """Show statistics of the current image."""
        if self.current_image is None:
            self.status_bar.showMessage("No image loaded")
            return
        stats = self.image_processor.get_statistics(self.current_image)
        self.status_bar.showMessage(f"Stats: {stats}")

    def show_about(self):
        """Show about dialog."""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About Image Analysis GUI",
            "Image Analysis GUI v1.0\n\n"
            "A tool for image analysis and processing.\n\n"
            "Created by: Byung Geun (BG) Jun\n"
            "Date: 2026-03-07"
        )
