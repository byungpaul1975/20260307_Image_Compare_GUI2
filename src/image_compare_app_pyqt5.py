"""
Image Compare Application
GUI application for comparing two images and visualizing pixel differences
Converted from Tkinter to PyQt5
"""

import sys
import os
import numpy as np
from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QLineEdit, QGroupBox,
    QFileDialog, QMessageBox, QFrame, QSizePolicy, QStatusBar
)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QWheelEvent

from PIL import Image


# ============== Clean Minimal Theme ==============
class Theme:
    BG_PRIMARY = "#2d2d2d"
    BG_SECONDARY = "#363636"
    BG_TERTIARY = "#404040"
    BG_CARD = "#3a3a3a"
    BORDER = "#4a4a4a"
    BORDER_LIGHT = "#555555"
    TEXT_PRIMARY = "#e8e8e8"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_MUTED = "#888888"
    ACCENT = "#6c9bce"
    ACCENT_HOVER = "#82afd8"
    CANVAS_BG = "#1e1e1e"
    MARKER_COLOR = "#ff6b6b"


GLOBAL_STYLESHEET = f"""
    QMainWindow {{ background-color: {Theme.BG_PRIMARY}; }}
    QWidget {{ background-color: {Theme.BG_PRIMARY}; color: {Theme.TEXT_PRIMARY};
              font-family: 'Segoe UI'; font-size: 9pt; }}
    QGroupBox {{ background-color: {Theme.BG_CARD}; border: 1px solid {Theme.BORDER};
                border-radius: 3px; margin-top: 14px; padding: 8px; font-size: 10pt; }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left;
                       padding: 2px 8px; color: {Theme.TEXT_PRIMARY}; }}
    QPushButton {{ background-color: {Theme.BG_TERTIARY}; color: {Theme.TEXT_PRIMARY};
                  border: none; padding: 6px 12px; font-size: 9pt; border-radius: 2px; }}
    QPushButton:hover {{ background-color: {Theme.BORDER_LIGHT}; }}
    QPushButton:pressed {{ background-color: {Theme.BORDER}; }}
    QPushButton[accent="true"] {{ background-color: {Theme.ACCENT}; color: #ffffff; }}
    QPushButton[accent="true"]:hover {{ background-color: {Theme.ACCENT_HOVER}; }}
    QPushButton[small="true"] {{ padding: 4px 8px; }}
    QLineEdit {{ background-color: {Theme.BG_SECONDARY}; color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER}; padding: 3px; }}
    QLabel {{ background-color: transparent; }}
    QLabel[muted="true"] {{ color: {Theme.TEXT_MUTED}; }}
    QLabel[card="true"] {{ color: {Theme.TEXT_SECONDARY}; font-family: 'Consolas'; }}
    QLabel[pixel="true"] {{ background-color: {Theme.BG_SECONDARY}; color: {Theme.TEXT_PRIMARY};
                           font-family: 'Consolas'; font-size: 10pt; padding: 2px 4px; }}
    QStatusBar {{ background-color: {Theme.BG_PRIMARY}; color: {Theme.TEXT_MUTED}; }}
    QFrame[separator="true"] {{ background-color: {Theme.BORDER}; }}
"""


class ImageCanvas(QWidget):
    """Custom canvas widget for displaying images with markers"""
    dragged = pyqtSignal(int, int)
    drag_started = pyqtSignal(int, int)
    drag_released = pyqtSignal(int, int, int, int)
    mouse_moved = pyqtSignal(int, int)
    wheel_scrolled = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)
        self._pixmap: Optional[QPixmap] = None
        self._marker_pos: Optional[Tuple[float, float]] = None
        self._drag_active = False
        self._drag_start = QPoint(0, 0)
        self._press_pos = QPoint(0, 0)

    def set_pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self.update()

    def set_marker(self, cx: float, cy: float):
        self._marker_pos = (cx, cy)
        self.update()

    def clear_marker(self):
        self._marker_pos = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(Theme.CANVAS_BG))
        if self._pixmap:
            x = (self.width() - self._pixmap.width()) // 2
            y = (self.height() - self._pixmap.height()) // 2
            painter.drawPixmap(x, y, self._pixmap)
        if self._marker_pos:
            cx, cy = self._marker_pos
            ms = 6
            pen = QPen(QColor(Theme.MARKER_COLOR), 2)
            painter.setPen(pen)
            painter.drawEllipse(int(cx - ms), int(cy - ms), ms * 2, ms * 2)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(int(cx - ms - 3), int(cy), int(cx + ms + 3), int(cy))
            painter.drawLine(int(cx), int(cy - ms - 3), int(cx), int(cy + ms + 3))
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_start = event.pos()
            self._press_pos = event.pos()
            self.drag_started.emit(event.x(), event.y())

    def mouseMoveEvent(self, event):
        if self._drag_active:
            dx = event.x() - self._drag_start.x()
            dy = event.y() - self._drag_start.y()
            self.dragged.emit(dx, dy)
            self._drag_start = event.pos()
        self.mouse_moved.emit(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drag_active:
            self._drag_active = False
            self.drag_released.emit(
                event.x(), event.y(),
                self._press_pos.x(), self._press_pos.y()
            )

    def wheelEvent(self, event: QWheelEvent):
        self.wheel_scrolled.emit(event.angleDelta().y())


class ImagePanel(QGroupBox):
    """Panel containing image canvas with info labels"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.base_title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(4)

        info_layout = QHBoxLayout()
        self.size_label = QLabel("")
        self.size_label.setProperty("card", True)
        self.view_label = QLabel("")
        self.view_label.setProperty("card", True)
        self.view_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()
        info_layout.addWidget(self.view_label)
        layout.addLayout(info_layout)

        self.canvas = ImageCanvas()
        layout.addWidget(self.canvas)
        self.image: Optional[Image.Image] = None

    def set_image(self, image: Optional[Image.Image], filename: str = None):
        self.image = image
        if image:
            w, h = image.size
            self.size_label.setText(f"{w} \u00d7 {h}")
            if filename:
                self._set_title_with_filename(filename)
        else:
            self.size_label.setText("")
            self.setTitle(self.base_title)

    def _set_title_with_filename(self, filename: str):
        basename = os.path.basename(filename)
        if len(basename) > 25:
            basename = basename[:22] + "..."
        self.setTitle(f"{self.base_title}: {basename}")

    def display(self, crop_box, display_size):
        if self.image is None:
            return
        try:
            cropped = self.image.crop(crop_box)
            resized = cropped.resize(display_size, Image.Resampling.NEAREST)
            if resized.mode == 'RGB':
                data = resized.tobytes("raw", "RGB")
                qimg = QImage(data, resized.width, resized.height, resized.width * 3, QImage.Format_RGB888)
            elif resized.mode == 'RGBA':
                data = resized.tobytes("raw", "RGBA")
                qimg = QImage(data, resized.width, resized.height, resized.width * 4, QImage.Format_RGBA8888)
            elif resized.mode == 'L':
                data = resized.tobytes("raw", "L")
                qimg = QImage(data, resized.width, resized.height, resized.width, QImage.Format_Grayscale8)
            else:
                resized = resized.convert('RGB')
                data = resized.tobytes("raw", "RGB")
                qimg = QImage(data, resized.width, resized.height, resized.width * 3, QImage.Format_RGB888)
            self.canvas.set_pixmap(QPixmap.fromImage(qimg))
            x1, y1, x2, y2 = crop_box
            self.view_label.setText(f"({x1},{y1}) {x2 - x1}\u00d7{y2 - y1}")
        except Exception as e:
            print(f"Display error: {e}")

    def show_marker(self, img_x, img_y, crop_box, display_size):
        x1, y1, x2, y2 = crop_box
        if not (x1 <= img_x < x2 and y1 <= img_y < y2):
            self.canvas.clear_marker()
            return
        offset_x = (self.canvas.width() - display_size[0]) // 2
        offset_y = (self.canvas.height() - display_size[1]) // 2
        rel_x = (img_x + 0.5 - x1) * display_size[0] / (x2 - x1)
        rel_y = (img_y + 0.5 - y1) * display_size[1] / (y2 - y1)
        self.canvas.set_marker(offset_x + rel_x, offset_y + rel_y)

    def clear_marker(self):
        self.canvas.clear_marker()


class ImageCompareApp(QMainWindow):
    """Main GUI application class for image comparison"""

    DEFAULT_VIEW_SIZE = 100
    MIN_ZOOM = 0.01
    MAX_ZOOM = 10.0
    ZOOM_STEP = 0.1
    NORMALIZATION_TARGET = 30000

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meta Platform: Image Compare Tool")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(900, 500)

        self.image1: Optional[Image.Image] = None
        self.image2: Optional[Image.Image] = None
        self.diff_image: Optional[Image.Image] = None
        self.image1_raw: Optional[np.ndarray] = None
        self.image2_raw: Optional[np.ndarray] = None
        self.image1_raw_original: Optional[np.ndarray] = None
        self.image2_raw_original: Optional[np.ndarray] = None
        self.diff_raw: Optional[np.ndarray] = None
        self.is_normalized = False

        self.zoom_level = 1.0
        self.view_center_x = 0
        self.view_center_y = 0
        self.image_size = (0, 0)
        self.clicked_pixel_x: Optional[int] = None
        self.clicked_pixel_y: Optional[int] = None

        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._create_control_panel(main_layout)
        self._create_image_panels(main_layout)
        self._create_pixel_bar(main_layout)
        self._create_status_bar()

    @staticmethod
    def _separator() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedWidth(1)
        sep.setProperty("separator", True)
        return sep

    def _create_control_panel(self, parent_layout):
        control = QWidget()
        control.setFixedHeight(44)
        lay = QHBoxLayout(control)
        lay.setContentsMargins(12, 6, 12, 6)

        btn_load1 = QPushButton("Load Image 1")
        btn_load1.clicked.connect(self._load_image1)
        lay.addWidget(btn_load1)
        btn_load2 = QPushButton("Load Image 2")
        btn_load2.clicked.connect(self._load_image2)
        lay.addWidget(btn_load2)
        lay.addWidget(self._separator())

        self.norm_btn = QPushButton("Normalize")
        self.norm_btn.setProperty("accent", True)
        self.norm_btn.clicked.connect(self._normalize_images)
        lay.addWidget(self.norm_btn)
        self.norm_status_label = QLabel("")
        self.norm_status_label.setProperty("muted", True)
        lay.addWidget(self.norm_status_label)
        lay.addWidget(self._separator())

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_images)
        lay.addWidget(btn_save)
        lay.addWidget(self._separator())

        lbl_zoom = QLabel("Zoom")
        lbl_zoom.setProperty("muted", True)
        lay.addWidget(lbl_zoom)
        btn_zo = QPushButton("\u2212")
        btn_zo.setFixedWidth(28)
        btn_zo.setProperty("small", True)
        btn_zo.clicked.connect(self._zoom_out)
        lay.addWidget(btn_zo)
        self.zoom_entry = QLineEdit("100")
        self.zoom_entry.setFixedWidth(50)
        self.zoom_entry.setAlignment(Qt.AlignCenter)
        self.zoom_entry.returnPressed.connect(self._on_zoom_entry)
        lay.addWidget(self.zoom_entry)
        lbl_pct = QLabel("%")
        lbl_pct.setProperty("muted", True)
        lay.addWidget(lbl_pct)
        btn_zi = QPushButton("+")
        btn_zi.setFixedWidth(28)
        btn_zi.setProperty("small", True)
        btn_zi.clicked.connect(self._zoom_in)
        lay.addWidget(btn_zi)
        lay.addWidget(self._separator())

        btn_center = QPushButton("Center")
        btn_center.setProperty("small", True)
        btn_center.clicked.connect(self._go_to_center)
        lay.addWidget(btn_center)
        btn_fit = QPushButton("Fit")
        btn_fit.setProperty("small", True)
        btn_fit.clicked.connect(self._fit_to_window)
        lay.addWidget(btn_fit)
        lay.addStretch()
        parent_layout.addWidget(control)

    def _create_image_panels(self, parent_layout):
        pw = QWidget()
        grid = QGridLayout(pw)
        grid.setContentsMargins(8, 4, 8, 4)
        grid.setSpacing(6)
        self.panel1 = ImagePanel("Image 1")
        self.panel2 = ImagePanel("Image 2")
        self.panel_diff = ImagePanel("Difference")
        grid.addWidget(self.panel1, 0, 0)
        grid.addWidget(self.panel2, 0, 1)
        grid.addWidget(self.panel_diff, 0, 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        parent_layout.addWidget(pw, 1)

    def _create_pixel_bar(self, parent_layout):
        bar = QWidget()
        bar.setStyleSheet(f"background-color: {Theme.BG_CARD};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 6, 12, 6)
        lbl = QLabel("Pixel")
        lbl.setProperty("muted", True)
        lay.addWidget(lbl)
        self.pixel_info_label = QLabel("Click on image to see values")
        self.pixel_info_label.setProperty("pixel", True)
        lay.addWidget(self.pixel_info_label)
        lay.addStretch()
        parent_layout.addWidget(bar)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("muted", True)
        self.position_label = QLabel("")
        self.position_label.setProperty("muted", True)
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.position_label)

    def _bind_events(self):
        for panel in [self.panel1, self.panel2, self.panel_diff]:
            panel.canvas.wheel_scrolled.connect(self._on_mouse_wheel)
            panel.canvas.dragged.connect(self._on_drag)
            panel.canvas.drag_released.connect(self._on_click_release)
            panel.canvas.mouse_moved.connect(self._on_mouse_move)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_display()

    # ── Image Loading ──────────────────────────────────────────

    def _load_image1(self):
        fp = self._open_file_dialog()
        if fp:
            self.image1 = self._load_image(fp, store_raw='image1')
            if self.image1:
                self.panel1.set_image(self.image1, filename=fp)
                self._update_image_size()
                self._calculate_diff()
                self._go_to_center()
                self.status_label.setText(f"Image 1 loaded: {fp}")

    def _load_image2(self):
        fp = self._open_file_dialog()
        if fp:
            self.image2 = self._load_image(fp, store_raw='image2')
            if self.image2:
                self.panel2.set_image(self.image2, filename=fp)
                self._update_image_size()
                self._calculate_diff()
                self._go_to_center()
                self.status_label.setText(f"Image 2 loaded: {fp}")

    def _open_file_dialog(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "All supported (*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.gif *.csv);;"
            "Image files (*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.gif);;"
            "CSV files (*.csv);;All files (*.*)")
        return fp if fp else None

    def _load_csv_as_image(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                sample = f.read(4096)
            delimiter = ','
            for delim in [',', '\t', ';', ' ']:
                lines = sample.strip().split('\n')
                if len(lines) > 0 and len(lines[0].split(delim)) > 1:
                    delimiter = delim
                    break
            skip_rows = 0
            with open(filepath, 'r', encoding='utf-8-sig') as f:
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
            arr = np.loadtxt(filepath, delimiter=delimiter, skiprows=skip_rows)
            if arr.ndim == 1:
                arr = arr.reshape(1, -1)
            return arr
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV: {e}")
            return None

    def _load_image(self, filepath, store_raw=None):
        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.csv':
                arr = self._load_csv_as_image(filepath)
                if arr is None:
                    return None
                arr_min, arr_max = float(np.min(arr)), float(np.max(arr))
                if arr_max <= 65535 and arr_min >= 0 and np.issubdtype(arr.dtype, np.integer):
                    raw = arr.astype(np.uint16)
                else:
                    if arr_max - arr_min > 0:
                        raw = ((arr - arr_min) / (arr_max - arr_min) * 65535).astype(np.uint16)
                    else:
                        raw = np.zeros_like(arr, dtype=np.uint16)
                if store_raw == 'image1':
                    self.image1_raw = raw.copy()
                elif store_raw == 'image2':
                    self.image2_raw = raw.copy()
                if arr_max - arr_min > 0:
                    arr_display = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)
                else:
                    arr_display = np.zeros_like(arr, dtype=np.uint8)
                return Image.fromarray(arr_display, mode='L')

            image = Image.open(filepath)
            if image.mode == 'I;16':
                arr = np.array(image, dtype=np.uint16)
                if store_raw == 'image1':
                    self.image1_raw = arr.copy()
                elif store_raw == 'image2':
                    self.image2_raw = arr.copy()
                arr_display = (arr.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                image = Image.fromarray(arr_display)
            elif image.mode == 'I':
                arr = np.array(image, dtype=np.int32)
                if store_raw == 'image1':
                    self.image1_raw = np.clip(arr, 0, 65535).astype(np.uint16)
                elif store_raw == 'image2':
                    self.image2_raw = np.clip(arr, 0, 65535).astype(np.uint16)
                arr_display = (np.clip(arr, 0, 65535).astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                image = Image.fromarray(arr_display)
            else:
                if image.mode not in ['RGB', 'RGBA', 'L']:
                    image = image.convert('RGB')
                arr = np.array(
                    image.convert('L') if image.mode in ['RGB', 'RGBA'] else image,
                    dtype=np.uint8)
                if store_raw == 'image1':
                    self.image1_raw = (arr.astype(np.uint16) * 256)
                elif store_raw == 'image2':
                    self.image2_raw = (arr.astype(np.uint16) * 256)
            return image
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {e}")
            return None

    # ── Diff Calculation ───────────────────────────────────────

    def _update_image_size(self):
        if self.image1:
            self.image_size = self.image1.size
        elif self.image2:
            self.image_size = self.image2.size

    def _calculate_diff(self):
        if self.image1 is None or self.image2 is None:
            self.diff_image = None
            self.diff_raw = None
            self.panel_diff.set_image(None)
            return
        try:
            if self.image1_raw is not None and self.image2_raw is not None:
                arr1 = self.image1_raw.astype(np.float32)
                arr2 = self.image2_raw.astype(np.float32)
                if arr1.shape != arr2.shape:
                    min_h = min(arr1.shape[0], arr2.shape[0])
                    min_w = min(arr1.shape[1], arr2.shape[1])
                    arr1 = arr1[:min_h, :min_w]
                    arr2 = arr2[:min_h, :min_w]
                    QMessageBox.warning(self, "Size Mismatch",
                        "Image sizes differ. Using smaller dimensions.")
            else:
                s1, s2 = self.image1.size, self.image2.size
                if s1 != s2:
                    QMessageBox.warning(self, "Size Mismatch",
                        f"Image sizes differ: {s1} vs {s2}\nUsing smaller dimensions.")
                    mw, mh = min(s1[0], s2[0]), min(s1[1], s2[1])
                    i1c = self.image1.crop((0, 0, mw, mh))
                    i2c = self.image2.crop((0, 0, mw, mh))
                else:
                    i1c, i2c = self.image1, self.image2
                arr1 = np.array(i1c.convert('L'), dtype=np.float32) * 256
                arr2 = np.array(i2c.convert('L'), dtype=np.float32) * 256

            self.diff_raw = arr1 - arr2
            diff_colored = np.zeros((*self.diff_raw.shape, 3), dtype=np.uint8)

            pos_mask = self.diff_raw >= 0
            if np.any(pos_mask):
                mp = self.diff_raw[pos_mask].max()
                if mp > 0:
                    gi = np.clip(self.diff_raw / mp * 255, 0, 255).astype(np.uint8)
                    diff_colored[:, :, 1] = np.where(pos_mask, gi, 0)
            neg_mask = self.diff_raw < 0
            if np.any(neg_mask):
                mn = self.diff_raw[neg_mask].min()
                if mn < 0:
                    ri = np.clip(np.abs(self.diff_raw) / np.abs(mn) * 255, 0, 255).astype(np.uint8)
                    diff_colored[:, :, 0] = np.where(neg_mask, ri, 0)

            self.diff_image = Image.fromarray(diff_colored)
            self.panel_diff.set_image(self.diff_image)
            self.status_label.setText(
                f"Difference (16-bit): Min={self.diff_raw.min():.0f}, Max={self.diff_raw.max():.0f}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate difference: {e}")

    # ── Display ────────────────────────────────────────────────

    def _get_crop_box(self):
        vs = int(self.DEFAULT_VIEW_SIZE / self.zoom_level)
        hs = vs // 2
        x1 = max(0, self.view_center_x - hs)
        y1 = max(0, self.view_center_y - hs)
        x2 = min(self.image_size[0], self.view_center_x + hs)
        y2 = min(self.image_size[1], self.view_center_y + hs)
        return (x1, y1, x2, y2)

    def _get_display_size(self):
        cw = self.panel1.canvas.width()
        ch = self.panel1.canvas.height()
        s = min(cw, ch) - 20
        return (max(100, s), max(100, s))

    def _update_display(self):
        if self.image_size[0] == 0:
            return
        crop_box = self._get_crop_box()
        display_size = self._get_display_size()
        self.panel1.display(crop_box, display_size)
        self.panel2.display(crop_box, display_size)
        self.panel_diff.display(crop_box, display_size)
        if self.clicked_pixel_x is not None and self.clicked_pixel_y is not None:
            self._show_markers(self.clicked_pixel_x, self.clicked_pixel_y)
        self.zoom_entry.setText(f"{int(self.zoom_level * 100)}")

    # ── Zoom / Navigation ─────────────────────────────────────

    def _on_zoom_entry(self):
        try:
            v = self.zoom_entry.text().replace('%', '').strip()
            zp = float(v)
            zp = max(1, min(zp, self.MAX_ZOOM * 100))
            self.zoom_level = zp / 100.0
            self._update_display()
        except ValueError:
            self.zoom_entry.setText(f"{int(self.zoom_level * 100)}")

    def _zoom_in(self):
        self.zoom_level = min(self.MAX_ZOOM, self.zoom_level + self.ZOOM_STEP)
        self._update_display()

    def _zoom_out(self):
        self.zoom_level = max(self.MIN_ZOOM, self.zoom_level - self.ZOOM_STEP)
        self._update_display()

    def _go_to_center(self):
        if self.image_size[0] > 0:
            self.view_center_x = self.image_size[0] // 2
            self.view_center_y = self.image_size[1] // 2
            self.zoom_level = 1.0
            self._update_display()

    def _fit_to_window(self):
        if self.image_size[0] > 0:
            self.view_center_x = self.image_size[0] // 2
            self.view_center_y = self.image_size[1] // 2
            cs = min(self.panel1.canvas.width(), self.panel1.canvas.height()) - 20
            self.zoom_level = cs / max(self.image_size)
            self._update_display()

    # ── Mouse Events ───────────────────────────────────────────

    def _on_mouse_wheel(self, delta):
        if delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    def _on_drag(self, dx, dy):
        if self.image_size[0] > 0:
            vs = int(self.DEFAULT_VIEW_SIZE / self.zoom_level)
            scale = vs / self._get_display_size()[0]
            self.view_center_x = max(0, min(self.image_size[0],
                                            self.view_center_x - int(dx * scale)))
            self.view_center_y = max(0, min(self.image_size[1],
                                            self.view_center_y - int(dy * scale)))
            self._update_display()

    def _on_click_release(self, x, y, start_x, start_y):
        dx = abs(x - start_x)
        dy = abs(y - start_y)
        if dx < 5 and dy < 5:
            self._show_pixel_values(x, y)

    def _on_mouse_move(self, x, y):
        if self.image_size[0] > 0:
            crop_box = self._get_crop_box()
            ds = self._get_display_size()
            cw = self.panel1.canvas.width()
            ch = self.panel1.canvas.height()
            ox = (cw - ds[0]) // 2
            oy = (ch - ds[1]) // 2
            rx, ry = x - ox, y - oy
            if 0 <= rx < ds[0] and 0 <= ry < ds[1]:
                ix = int(crop_box[0] + rx * (crop_box[2] - crop_box[0]) / ds[0])
                iy = int(crop_box[1] + ry * (crop_box[3] - crop_box[1]) / ds[1])
                self.position_label.setText(f"Position: ({ix}, {iy})")
            else:
                self.position_label.setText("")

    # ── Pixel Info ─────────────────────────────────────────────

    def _show_pixel_values(self, event_x, event_y):
        if self.image_size[0] == 0:
            return
        crop_box = self._get_crop_box()
        ds = self._get_display_size()
        cw = self.panel1.canvas.width()
        ch = self.panel1.canvas.height()
        ox = (cw - ds[0]) // 2
        oy = (ch - ds[1]) // 2
        rx, ry = event_x - ox, event_y - oy

        if not (0 <= rx < ds[0] and 0 <= ry < ds[1]):
            return

        img_x = int(crop_box[0] + rx * (crop_box[2] - crop_box[0]) / ds[0])
        img_y = int(crop_box[1] + ry * (crop_box[3] - crop_box[1]) / ds[1])

        pv = []
        # Image 1
        if self.image1_raw is not None:
            try:
                h, w = self.image1_raw.shape[:2]
                if 0 <= img_x < w and 0 <= img_y < h:
                    pv.append(f"Img1: {self.image1_raw[img_y, img_x]}")
                else:
                    pv.append("Img1: -")
            except Exception:
                pv.append("Img1: -")
        elif self.image1 is not None:
            try:
                w, h = self.image1.size
                if 0 <= img_x < w and 0 <= img_y < h:
                    p = self.image1.getpixel((img_x, img_y))
                    if isinstance(p, tuple):
                        p = p[0]
                    pv.append(f"Img1: {p * 256}")
                else:
                    pv.append("Img1: -")
            except Exception:
                pv.append("Img1: -")
        else:
            pv.append("Img1: -")

        # Image 2
        if self.image2_raw is not None:
            try:
                h, w = self.image2_raw.shape[:2]
                if 0 <= img_x < w and 0 <= img_y < h:
                    pv.append(f"Img2: {self.image2_raw[img_y, img_x]}")
                else:
                    pv.append("Img2: -")
            except Exception:
                pv.append("Img2: -")
        elif self.image2 is not None:
            try:
                w, h = self.image2.size
                if 0 <= img_x < w and 0 <= img_y < h:
                    p = self.image2.getpixel((img_x, img_y))
                    if isinstance(p, tuple):
                        p = p[0]
                    pv.append(f"Img2: {p * 256}")
                else:
                    pv.append("Img2: -")
            except Exception:
                pv.append("Img2: -")
        else:
            pv.append("Img2: -")

        # Difference
        if self.diff_raw is not None:
            try:
                h, w = self.diff_raw.shape[:2]
                if 0 <= img_x < w and 0 <= img_y < h:
                    pv.append(f"Diff: {self.diff_raw[img_y, img_x]:.0f}")
                else:
                    pv.append("Diff: -")
            except Exception:
                pv.append("Diff: -")
        else:
            pv.append("Diff: -")

        self.pixel_info_label.setText(f"({img_x}, {img_y})  |  " + "  |  ".join(pv))
        self.clicked_pixel_x = img_x
        self.clicked_pixel_y = img_y
        self._show_markers(img_x, img_y)

    def _show_markers(self, img_x, img_y):
        crop_box = self._get_crop_box()
        ds = self._get_display_size()
        self.panel1.show_marker(img_x, img_y, crop_box, ds)
        self.panel2.show_marker(img_x, img_y, crop_box, ds)
        self.panel_diff.show_marker(img_x, img_y, crop_box, ds)

    # ── Normalization ──────────────────────────────────────────

    def _normalize_images(self):
        if self.image1 is None and self.image2 is None:
            QMessageBox.warning(self, "Warning", "No images loaded to normalize.")
            return
        try:
            if self.is_normalized:
                self._restore_original_images()
                return
            if self.image1_raw is not None:
                self.image1_raw_original = self.image1_raw.copy()
            if self.image2_raw is not None:
                self.image2_raw_original = self.image2_raw.copy()
            nc = 0
            if self.image1 is not None:
                ni, f1 = self._normalize_single_image(self.image1)
                if ni is not None:
                    self.image1 = ni
                    self.panel1.set_image(self.image1)
                    if self.image1_raw is not None:
                        self.image1_raw = np.clip(
                            self.image1_raw.astype(np.float32) * f1, 0, 65535).astype(np.uint16)
                    nc += 1
            if self.image2 is not None:
                ni, f2 = self._normalize_single_image(self.image2)
                if ni is not None:
                    self.image2 = ni
                    self.panel2.set_image(self.image2)
                    if self.image2_raw is not None:
                        self.image2_raw = np.clip(
                            self.image2_raw.astype(np.float32) * f2, 0, 65535).astype(np.uint16)
                    nc += 1
            if nc > 0:
                self._calculate_diff()
                self._update_display()
                self.is_normalized = True
                self.norm_status_label.setText("\u2713 ON")
                self.norm_btn.setText("Restore")
                self.status_label.setText(f"Normalized (target={self.NORMALIZATION_TARGET})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Normalization failed: {e}")

    def _restore_original_images(self):
        try:
            rc = 0
            if self.image1_raw_original is not None:
                self.image1_raw = self.image1_raw_original.copy()
                ad = (self.image1_raw.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                self.image1 = Image.fromarray(ad)
                self.panel1.set_image(self.image1)
                rc += 1
            if self.image2_raw_original is not None:
                self.image2_raw = self.image2_raw_original.copy()
                ad = (self.image2_raw.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                self.image2 = Image.fromarray(ad)
                self.panel2.set_image(self.image2)
                rc += 1
            if rc > 0:
                self._calculate_diff()
                self._update_display()
                self.is_normalized = False
                self.norm_status_label.setText("")
                self.norm_btn.setText("Normalize")
                self.status_label.setText("Restored to original images")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore: {e}")

    def _normalize_single_image(self, image):
        try:
            arr = np.array(image, dtype=np.float32)
            h, w = arr.shape[:2]
            cx, cy = w // 2, h // 2
            hs = 50
            x1, x2 = max(0, cx - hs), min(w, cx + hs)
            y1, y2 = max(0, cy - hs), min(h, cy + hs)
            if len(arr.shape) == 3:
                cr = arr[y1:y2, x1:x2, 0]
            else:
                cr = arr[y1:y2, x1:x2]
            ca = np.mean(cr)
            if ca == 0:
                QMessageBox.warning(self, "Warning",
                    "Center region average is 0, cannot normalize.")
                return None, 0.0
            ca16 = ca * 256
            factor = self.NORMALIZATION_TARGET / ca16
            na = np.clip(arr * factor, 0, 255).astype(np.uint8)
            if len(arr.shape) == 3:
                return Image.fromarray(na, mode='RGB'), factor
            else:
                return Image.fromarray(na, mode='L'), factor
        except Exception as e:
            print(f"Normalization error: {e}")
            return None, 0.0

    # ── Save ───────────────────────────────────────────────────

    def _save_images(self):
        if self.image1 is None and self.image2 is None:
            QMessageBox.warning(self, "Warning", "No images to save.")
            return
        save_dir = QFileDialog.getExistingDirectory(self, "Select folder to save images")
        if not save_dir:
            return
        saved = []
        try:
            if self.image1_raw is not None:
                fp = os.path.join(save_dir, "image1_normalized.tif")
                scaled = np.clip(self.image1_raw.astype(np.uint32) * 16, 0, 65535).astype(np.uint16)
                Image.fromarray(scaled).save(fp)
                saved.append("image1_normalized.tif")
            elif self.image1 is not None:
                fp = os.path.join(save_dir, "image1.png")
                self.image1.save(fp)
                saved.append("image1.png")
            if self.image2_raw is not None:
                fp = os.path.join(save_dir, "image2_normalized.tif")
                scaled = np.clip(self.image2_raw.astype(np.uint32) * 16, 0, 65535).astype(np.uint16)
                Image.fromarray(scaled).save(fp)
                saved.append("image2_normalized.tif")
            elif self.image2 is not None:
                fp = os.path.join(save_dir, "image2.png")
                self.image2.save(fp)
                saved.append("image2.png")
            if self.diff_raw is not None:
                fp = os.path.join(save_dir, "diff_image.tif")
                ds = self.diff_raw.astype(np.float64) * 16 + 30000
                Image.fromarray(np.clip(ds, 0, 65535).astype(np.uint16)).save(fp)
                saved.append("diff_image.tif")
                if self.diff_image is not None:
                    fp2 = os.path.join(save_dir, "diff_visualization.png")
                    self.diff_image.save(fp2)
                    saved.append("diff_visualization.png")
            if saved:
                self.status_label.setText(f"Saved: {', '.join(saved)}")
                QMessageBox.information(self, "Save Complete",
                    f"Images saved to:\n{save_dir}\n\nFiles:\n" + "\n".join(saved))
            else:
                QMessageBox.warning(self, "Warning", "No images were saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save images: {e}")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)
    window = ImageCompareApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
