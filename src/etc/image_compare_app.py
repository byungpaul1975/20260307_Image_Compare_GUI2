"""
Image Compare Application
GUI application for comparing two images and visualizing pixel differences
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import csv
import os
from typing import Optional, Tuple


# ============== Clean Minimal Theme ==============
class Theme:
    """Clean minimal theme"""
    # Background colors (soft gray tones)
    BG_PRIMARY = "#2d2d2d"
    BG_SECONDARY = "#363636"
    BG_TERTIARY = "#404040"
    BG_CARD = "#3a3a3a"

    # Border
    BORDER = "#4a4a4a"
    BORDER_LIGHT = "#555555"

    # Text
    TEXT_PRIMARY = "#e8e8e8"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_MUTED = "#888888"

    # Accent (restrained use)
    ACCENT = "#6c9bce"
    ACCENT_HOVER = "#82afd8"

    # Canvas
    CANVAS_BG = "#1e1e1e"

    # Marker
    MARKER_COLOR = "#ff6b6b"


def setup_theme(root):
    """Setup clean minimal style"""
    style = ttk.Style()
    style.theme_use('clam')

    # Frame
    style.configure("TFrame", background=Theme.BG_PRIMARY)
    style.configure("Card.TFrame", background=Theme.BG_CARD)

    # LabelFrame (image panels)
    style.configure("TLabelframe",
                    background=Theme.BG_CARD,
                    bordercolor=Theme.BORDER,
                    borderwidth=1,
                    relief="flat")
    style.configure("TLabelframe.Label",
                    background=Theme.BG_CARD,
                    foreground=Theme.TEXT_PRIMARY,
                    font=('Segoe UI', 10))

    # Label
    style.configure("TLabel",
                    background=Theme.BG_PRIMARY,
                    foreground=Theme.TEXT_PRIMARY,
                    font=('Segoe UI', 9))
    style.configure("Card.TLabel",
                    background=Theme.BG_CARD,
                    foreground=Theme.TEXT_SECONDARY,
                    font=('Consolas', 9))
    style.configure("Muted.TLabel",
                    background=Theme.BG_PRIMARY,
                    foreground=Theme.TEXT_MUTED,
                    font=('Segoe UI', 9))
    style.configure("Pixel.TLabel",
                    background=Theme.BG_SECONDARY,
                    foreground=Theme.TEXT_PRIMARY,
                    font=('Consolas', 10))

    # Button (flat design)
    style.configure("TButton",
                    background=Theme.BG_TERTIARY,
                    foreground=Theme.TEXT_PRIMARY,
                    font=('Segoe UI', 9),
                    borderwidth=0,
                    padding=(12, 6))
    style.map("TButton",
              background=[('active', Theme.BORDER_LIGHT),
                         ('pressed', Theme.BORDER)])

    # Accent button
    style.configure("Accent.TButton",
                    background=Theme.ACCENT,
                    foreground="#ffffff",
                    font=('Segoe UI', 9),
                    borderwidth=0,
                    padding=(12, 6))
    style.map("Accent.TButton",
              background=[('active', Theme.ACCENT_HOVER)])

    # Small button
    style.configure("Small.TButton",
                    background=Theme.BG_TERTIARY,
                    foreground=Theme.TEXT_PRIMARY,
                    font=('Segoe UI', 9),
                    borderwidth=0,
                    padding=(8, 4))
    style.map("Small.TButton",
              background=[('active', Theme.BORDER_LIGHT)])

    # Separator
    style.configure("TSeparator", background=Theme.BORDER)

    # Entry
    style.configure("TEntry",
                    fieldbackground=Theme.BG_SECONDARY,
                    foreground=Theme.TEXT_PRIMARY,
                    borderwidth=1)

    return style


class ImagePanel:
    """Class to manage individual image panel"""

    def __init__(self, parent: tk.Frame, title: str):
        self.title = title
        self.base_title = title  # Store original title
        self.frame = ttk.LabelFrame(parent, text=title, padding=8)

        # Info label frame
        self.info_frame = ttk.Frame(self.frame, style="Card.TFrame")
        self.info_frame.pack(fill=tk.X, pady=(0, 4))

        # Image size label
        self.size_var = tk.StringVar(value="")
        self.size_label = ttk.Label(self.info_frame, textvariable=self.size_var,
                                     style="Card.TLabel")
        self.size_label.pack(side=tk.LEFT, padx=4)

        # Current view position label
        self.view_var = tk.StringVar(value="")
        self.view_label = ttk.Label(self.info_frame, textvariable=self.view_var,
                                     style="Card.TLabel")
        self.view_label.pack(side=tk.RIGHT, padx=4)

        self.canvas = tk.Canvas(self.frame, bg=Theme.CANVAS_BG, width=300, height=300,
                                highlightthickness=1, highlightbackground=Theme.BORDER)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image: Optional[Image.Image] = None
        self.photo_image: Optional[ImageTk.PhotoImage] = None
        self.canvas_image_id: Optional[int] = None
        self.marker_id: Optional[int] = None  # Click position marker

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def set_image(self, image: Image.Image, filename: str = None):
        """Set image with optional filename"""
        self.image = image
        if image:
            w, h = image.size
            self.size_var.set(f"{w} × {h}")
            # Update title with filename
            if filename:
                self.set_title_with_filename(filename)
        else:
            self.size_var.set("")
            self.frame.configure(text=self.base_title)

    def set_title_with_filename(self, filename: str):
        """Update panel title to show filename"""
        import os
        basename = os.path.basename(filename)
        # Truncate if too long
        if len(basename) > 25:
            basename = basename[:22] + "..."
        self.frame.configure(text=f"{self.base_title}: {basename}")

    def display(self, crop_box: Tuple[int, int, int, int], display_size: Tuple[int, int]):
        """Display cropped region on canvas"""
        if self.image is None:
            return

        try:
            cropped = self.image.crop(crop_box)
            resized = cropped.resize(display_size, Image.Resampling.NEAREST)
            self.photo_image = ImageTk.PhotoImage(resized)

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if self.canvas_image_id:
                self.canvas.delete(self.canvas_image_id)

            self.canvas_image_id = self.canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                anchor=tk.CENTER, image=self.photo_image
            )

            # Update view position info
            x1, y1, x2, y2 = crop_box
            view_w = x2 - x1
            view_h = y2 - y1
            self.view_var.set(f"({x1},{y1}) {view_w}×{view_h}")

        except Exception as e:
            print(f"Display error: {e}")

    def show_marker(self, img_x: int, img_y: int, crop_box: Tuple[int, int, int, int], display_size: Tuple[int, int]):
        """Show marker at clicked pixel position - centered on pixel"""
        # Delete existing marker
        if self.marker_id:
            self.canvas.delete(self.marker_id)
            self.marker_id = None

        x1, y1, x2, y2 = crop_box

        # Check if image coordinates are within current view area
        if not (x1 <= img_x < x2 and y1 <= img_y < y2):
            return

        # Convert image coordinates to canvas coordinates (center on pixel with +0.5)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        offset_x = (canvas_width - display_size[0]) // 2
        offset_y = (canvas_height - display_size[1]) // 2

        # Calculate pixel center coordinates (img_x + 0.5, img_y + 0.5)
        rel_x = (img_x + 0.5 - x1) * display_size[0] / (x2 - x1)
        rel_y = (img_y + 0.5 - y1) * display_size[1] / (y2 - y1)

        canvas_x = offset_x + rel_x
        canvas_y = offset_y + rel_y

        # Draw cross marker (red)
        marker_size = 6
        self.marker_id = self.canvas.create_oval(
            canvas_x - marker_size, canvas_y - marker_size,
            canvas_x + marker_size, canvas_y + marker_size,
            outline=Theme.MARKER_COLOR, width=2
        )
        # Add crosshairs
        self.canvas.create_line(
            canvas_x - marker_size - 3, canvas_y,
            canvas_x + marker_size + 3, canvas_y,
            fill=Theme.MARKER_COLOR, width=1, tags='marker_cross'
        )
        self.canvas.create_line(
            canvas_x, canvas_y - marker_size - 3,
            canvas_x, canvas_y + marker_size + 3,
            fill=Theme.MARKER_COLOR, width=1, tags='marker_cross'
        )

    def clear_marker(self):
        """Clear marker"""
        if self.marker_id:
            self.canvas.delete(self.marker_id)
            self.marker_id = None
        self.canvas.delete('marker_cross')


class ImageCompareApp:
    """Main GUI application class for image comparison"""

    DEFAULT_VIEW_SIZE = 100
    MIN_ZOOM = 0.01  # Allow down to 0% (actually 1% is minimum)
    MAX_ZOOM = 10.0
    ZOOM_STEP = 0.1
    NORMALIZATION_TARGET = 30000  # Target value based on 16-bit (center 100x100 average)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Compare Tool")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)

        # Apply theme
        self.root.configure(bg=Theme.BG_PRIMARY)
        setup_theme(root)

        self.image1: Optional[Image.Image] = None
        self.image2: Optional[Image.Image] = None
        self.diff_image: Optional[Image.Image] = None

        # Preserve original image data (16-bit)
        self.image1_raw: Optional[np.ndarray] = None
        self.image2_raw: Optional[np.ndarray] = None
        # Backup of original data before normalization
        self.image1_raw_original: Optional[np.ndarray] = None
        self.image2_raw_original: Optional[np.ndarray] = None
        # Actual difference value array (img1 - img2, signed)
        self.diff_raw: Optional[np.ndarray] = None
        self.is_normalized = False

        self.zoom_level = 1.0
        self.view_center_x = 0
        self.view_center_y = 0
        self.image_size = (0, 0)

        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Store clicked pixel position
        self.clicked_pixel_x: Optional[int] = None
        self.clicked_pixel_y: Optional[int] = None

        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        """Setup UI components"""
        self._create_control_panel()
        self._create_image_panels()
        self._create_status_bar()

    def _create_control_panel(self):
        """Create control panel"""
        control_frame = ttk.Frame(self.root, padding=(12, 8))
        control_frame.pack(fill=tk.X)

        # Image load buttons
        ttk.Button(control_frame, text="Load Image 1",
                   command=self._load_image1).pack(side=tk.LEFT, padx=3)
        ttk.Button(control_frame, text="Load Image 2",
                   command=self._load_image2).pack(side=tk.LEFT, padx=3)

        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        # Normalization button
        self.norm_btn = ttk.Button(control_frame, text="Normalize",
                                    command=self._normalize_images, style="Accent.TButton")
        self.norm_btn.pack(side=tk.LEFT, padx=3)

        self.norm_status_var = tk.StringVar(value="")
        ttk.Label(control_frame, textvariable=self.norm_status_var,
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=4)

        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        # Save Images button
        ttk.Button(control_frame, text="Save",
                   command=self._save_images).pack(side=tk.LEFT, padx=3)

        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        # Zoom controls
        ttk.Label(control_frame, text="Zoom", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(control_frame, text="−", width=2,
                   command=self._zoom_out, style="Small.TButton").pack(side=tk.LEFT)

        self.zoom_var = tk.StringVar(value="100")
        self.zoom_entry = ttk.Entry(control_frame, textvariable=self.zoom_var,
                                     width=5, justify=tk.CENTER)
        self.zoom_entry.pack(side=tk.LEFT, padx=3)
        self.zoom_entry.bind("<Return>", self._on_zoom_entry)
        self.zoom_entry.bind("<FocusOut>", self._on_zoom_entry)

        ttk.Label(control_frame, text="%", style="Muted.TLabel").pack(side=tk.LEFT)

        ttk.Button(control_frame, text="+", width=2,
                   command=self._zoom_in, style="Small.TButton").pack(side=tk.LEFT, padx=(3, 0))

        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        # View controls
        ttk.Button(control_frame, text="Center",
                   command=self._go_to_center, style="Small.TButton").pack(side=tk.LEFT, padx=3)

        ttk.Button(control_frame, text="Fit",
                   command=self._fit_to_window, style="Small.TButton").pack(side=tk.LEFT, padx=3)

    def _create_image_panels(self):
        """Create image panels"""
        panels_frame = ttk.Frame(self.root)
        panels_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        panels_frame.columnconfigure(0, weight=1)
        panels_frame.columnconfigure(1, weight=1)
        panels_frame.columnconfigure(2, weight=1)
        panels_frame.rowconfigure(0, weight=1)

        self.panel1 = ImagePanel(panels_frame, "Image 1")
        self.panel1.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        self.panel2 = ImagePanel(panels_frame, "Image 2")
        self.panel2.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

        self.panel_diff = ImagePanel(panels_frame, "Difference")
        self.panel_diff.grid(row=0, column=2, sticky="nsew", padx=3, pady=3)

    def _create_status_bar(self):
        """Create status bar"""
        # Pixel value info display frame (bottom)
        pixel_frame = ttk.Frame(self.root, padding=(12, 8), style="Card.TFrame")
        pixel_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Label(pixel_frame, text="Pixel",
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 8))

        self.pixel_info_var = tk.StringVar(value="Click on image to see values")
        self.pixel_info_label = ttk.Label(pixel_frame, textvariable=self.pixel_info_var,
                                           style="Pixel.TLabel")
        self.pixel_info_label.pack(side=tk.LEFT)

        # Status bar
        status_frame = ttk.Frame(self.root, padding=(12, 6))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var,
                  style="Muted.TLabel").pack(side=tk.LEFT)

        self.position_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.position_var,
                  style="Muted.TLabel").pack(side=tk.RIGHT)

    def _bind_events(self):
        """Bind events"""
        for panel in [self.panel1, self.panel2, self.panel_diff]:
            panel.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
            panel.canvas.bind("<ButtonPress-1>", self._on_drag_start)
            panel.canvas.bind("<B1-Motion>", self._on_drag)
            panel.canvas.bind("<ButtonRelease-1>", self._on_click_release)
            panel.canvas.bind("<Motion>", self._on_mouse_move)
            panel.canvas.bind("<Configure>", self._on_resize)

    def _load_image1(self):
        """Load image 1"""
        filepath = self._open_file_dialog()
        if filepath:
            self.image1 = self._load_image(filepath, store_raw='image1')
            if self.image1:
                self.panel1.set_image(self.image1, filename=filepath)
                self._update_image_size()
                self._calculate_diff()
                self._go_to_center()
                self.status_var.set(f"Image 1 loaded: {filepath}")

    def _load_image2(self):
        """Load image 2"""
        filepath = self._open_file_dialog()
        if filepath:
            self.image2 = self._load_image(filepath, store_raw='image2')
            if self.image2:
                self.panel2.set_image(self.image2, filename=filepath)
                self._update_image_size()
                self._calculate_diff()
                self._go_to_center()
                self.status_var.set(f"Image 2 loaded: {filepath}")

    def _open_file_dialog(self) -> Optional[str]:
        """Open file dialog"""
        filetypes = [
            ("All supported files", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.gif *.csv"),
            ("Image files", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.gif"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        return filedialog.askopenfilename(filetypes=filetypes)

    def _load_csv_as_image(self, filepath: str) -> Optional[np.ndarray]:
        """Load CSV file as a 2D numpy array.

        Supports:
        - Comma, tab, semicolon, or space delimited files
        - Integer and float values
        - Automatically skips header rows that contain non-numeric data

        Returns:
            2D numpy array (float64) or None if failed.
        """
        try:
            # Try to detect delimiter and load
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                sample = f.read(4096)

            # Detect delimiter
            delimiter = ','
            for delim in [',', '\t', ';', ' ']:
                lines = sample.strip().split('\n')
                if len(lines) > 0 and len(lines[0].split(delim)) > 1:
                    delimiter = delim
                    break

            # Find where numeric data starts (skip header rows)
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
            messagebox.showerror("Error", f"Failed to load CSV: {e}")
            return None

    def _load_image(self, filepath: str, store_raw: str = None) -> Optional[Image.Image]:
        """Load image or CSV file - preserve 16-bit original data"""
        try:
            ext = os.path.splitext(filepath)[1].lower()

            # CSV file handling
            if ext == '.csv':
                arr = self._load_csv_as_image(filepath)
                if arr is None:
                    return None

                # Store raw data
                arr_min, arr_max = float(np.min(arr)), float(np.max(arr))

                if arr_max <= 65535 and arr_min >= 0 and np.issubdtype(arr.dtype, np.integer):
                    raw = arr.astype(np.uint16)
                else:
                    # Normalize to 0-65535 range for raw storage
                    if arr_max - arr_min > 0:
                        raw = ((arr - arr_min) / (arr_max - arr_min) * 65535).astype(np.uint16)
                    else:
                        raw = np.zeros_like(arr, dtype=np.uint16)

                if store_raw == 'image1':
                    self.image1_raw = raw.copy()
                elif store_raw == 'image2':
                    self.image2_raw = raw.copy()

                # Convert to 8-bit for display
                if arr_max - arr_min > 0:
                    arr_display = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)
                else:
                    arr_display = np.zeros_like(arr, dtype=np.uint8)

                image = Image.fromarray(arr_display, mode='L')
                return image

            # Standard image file handling
            image = Image.open(filepath)

            # Handle 16-bit images
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
                arr = np.array(image.convert('L') if image.mode in ['RGB', 'RGBA'] else image, dtype=np.uint8)
                if store_raw == 'image1':
                    self.image1_raw = (arr.astype(np.uint16) * 256)
                elif store_raw == 'image2':
                    self.image2_raw = (arr.astype(np.uint16) * 256)

            return image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
            return None

    def _update_image_size(self):
        """Update image size"""
        if self.image1:
            self.image_size = self.image1.size
        elif self.image2:
            self.image_size = self.image2.size

    def _calculate_diff(self):
        """Calculate pixel difference image - actual difference based on 16-bit (img1 - img2)"""
        if self.image1 is None or self.image2 is None:
            self.diff_image = None
            self.diff_raw = None
            self.panel_diff.set_image(None)
            return

        try:
            # Use 16-bit original data
            if self.image1_raw is not None and self.image2_raw is not None:
                arr1 = self.image1_raw.astype(np.float32)
                arr2 = self.image2_raw.astype(np.float32)

                # Handle different sizes
                if arr1.shape != arr2.shape:
                    min_h = min(arr1.shape[0], arr2.shape[0])
                    min_w = min(arr1.shape[1], arr2.shape[1])
                    arr1 = arr1[:min_h, :min_w]
                    arr2 = arr2[:min_h, :min_w]
                    messagebox.showwarning(
                        "Size Mismatch",
                        f"Image sizes differ. Using the smaller dimensions for comparison."
                    )
            else:
                # Convert 8-bit images to 16-bit scale
                img1_size = self.image1.size
                img2_size = self.image2.size

                if img1_size != img2_size:
                    messagebox.showwarning(
                        "Size Mismatch",
                        f"Image sizes differ: {img1_size} vs {img2_size}\n"
                        "Using the smaller dimensions for comparison."
                    )
                    min_width = min(img1_size[0], img2_size[0])
                    min_height = min(img1_size[1], img2_size[1])
                    img1_cropped = self.image1.crop((0, 0, min_width, min_height))
                    img2_cropped = self.image2.crop((0, 0, min_width, min_height))
                else:
                    img1_cropped = self.image1
                    img2_cropped = self.image2

                arr1 = np.array(img1_cropped.convert('L'), dtype=np.float32) * 256  # 8-bit to 16-bit
                arr2 = np.array(img2_cropped.convert('L'), dtype=np.float32) * 256

            # Calculate actual difference (signed: img1 - img2)
            self.diff_raw = arr1 - arr2

            # Visualization: color map based on difference values
            # diff_raw >= 0 (Image1 >= Image2): Green
            # diff_raw < 0 (Image1 < Image2): Red
            diff_colored = np.zeros((*self.diff_raw.shape, 3), dtype=np.uint8)

            # Positive difference (Image1 > Image2): Display in green channel
            positive_mask = self.diff_raw >= 0
            if np.any(positive_mask):
                max_positive = self.diff_raw[positive_mask].max()
                if max_positive > 0:
                    green_intensity = np.clip(self.diff_raw / max_positive * 255, 0, 255).astype(np.uint8)
                    diff_colored[:, :, 1] = np.where(positive_mask, green_intensity, 0)

            # Negative difference (Image1 < Image2): Display in red channel
            negative_mask = self.diff_raw < 0
            if np.any(negative_mask):
                min_negative = self.diff_raw[negative_mask].min()
                if min_negative < 0:
                    red_intensity = np.clip(np.abs(self.diff_raw) / np.abs(min_negative) * 255, 0, 255).astype(np.uint8)
                    diff_colored[:, :, 0] = np.where(negative_mask, red_intensity, 0)

            self.diff_image = Image.fromarray(diff_colored)
            self.panel_diff.set_image(self.diff_image)

            self.status_var.set(f"Difference (16-bit): Min={self.diff_raw.min():.0f}, Max={self.diff_raw.max():.0f}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate difference: {e}")

    def _get_crop_box(self) -> Tuple[int, int, int, int]:
        """Calculate crop box for current view"""
        view_size = int(self.DEFAULT_VIEW_SIZE / self.zoom_level)
        half_size = view_size // 2

        x1 = max(0, self.view_center_x - half_size)
        y1 = max(0, self.view_center_y - half_size)
        x2 = min(self.image_size[0], self.view_center_x + half_size)
        y2 = min(self.image_size[1], self.view_center_y + half_size)

        return (x1, y1, x2, y2)

    def _get_display_size(self) -> Tuple[int, int]:
        """Return display size"""
        canvas_width = self.panel1.canvas.winfo_width()
        canvas_height = self.panel1.canvas.winfo_height()
        size = min(canvas_width, canvas_height) - 20
        return (max(100, size), max(100, size))

    def _update_display(self):
        """Update all panels"""
        if self.image_size[0] == 0:
            return

        crop_box = self._get_crop_box()
        display_size = self._get_display_size()

        self.panel1.display(crop_box, display_size)
        self.panel2.display(crop_box, display_size)
        self.panel_diff.display(crop_box, display_size)

        # Update clicked position markers
        if self.clicked_pixel_x is not None and self.clicked_pixel_y is not None:
            self._show_markers(self.clicked_pixel_x, self.clicked_pixel_y)

        # Update zoom input field (without % symbol)
        self.zoom_var.set(f"{int(self.zoom_level * 100)}")

    def _on_zoom_entry(self, event=None):
        """Handle Enter or focus out on zoom input field"""
        try:
            value = self.zoom_var.get().replace('%', '').strip()
            zoom_percent = float(value)

            # Allow 0% or higher (minimum is actually 1%)
            if zoom_percent < 1:
                zoom_percent = 1
            elif zoom_percent > self.MAX_ZOOM * 100:
                zoom_percent = self.MAX_ZOOM * 100

            self.zoom_level = zoom_percent / 100.0
            self._update_display()
        except ValueError:
            # Restore current value on invalid input
            self.zoom_var.set(f"{int(self.zoom_level * 100)}")

    def _normalize_images(self):
        """Toggle image normalization - normalize/restore original"""
        if self.image1 is None and self.image2 is None:
            messagebox.showwarning("Warning", "No images loaded to normalize.")
            return

        try:
            # If already normalized, restore to original
            if self.is_normalized:
                self._restore_original_images()
                return

            # Backup original before normalization
            if self.image1_raw is not None:
                self.image1_raw_original = self.image1_raw.copy()
            if self.image2_raw is not None:
                self.image2_raw_original = self.image2_raw.copy()

            normalized_count = 0

            # Normalize Image 1
            if self.image1 is not None:
                norm_img1, factor1 = self._normalize_single_image(self.image1)
                if norm_img1 is not None:
                    self.image1 = norm_img1
                    self.panel1.set_image(self.image1)
                    # Also normalize 16-bit raw data
                    if self.image1_raw is not None:
                        self.image1_raw = np.clip(
                            self.image1_raw.astype(np.float32) * factor1,
                            0, 65535
                        ).astype(np.uint16)
                    normalized_count += 1
                    self.status_var.set(f"Image 1 normalized (factor: {factor1:.4f})")

            # Normalize Image 2
            if self.image2 is not None:
                norm_img2, factor2 = self._normalize_single_image(self.image2)
                if norm_img2 is not None:
                    self.image2 = norm_img2
                    self.panel2.set_image(self.image2)
                    # 16-bit raw 데이터도 정규화
                    if self.image2_raw is not None:
                        self.image2_raw = np.clip(
                            self.image2_raw.astype(np.float32) * factor2,
                            0, 65535
                        ).astype(np.uint16)
                    normalized_count += 1
                    self.status_var.set(f"Image 2 normalized (factor: {factor2:.4f})")

            # Recalculate difference image
            if normalized_count > 0:
                self._calculate_diff()
                self._update_display()
                self.is_normalized = True
                self.norm_status_var.set("✓ ON")
                self.norm_btn.configure(text="Restore")

                if self.image1 is not None and self.image2 is not None:
                    self.status_var.set(f"Normalized (target={self.NORMALIZATION_TARGET})")

        except Exception as e:
            messagebox.showerror("Error", f"Normalization failed: {e}")

    def _restore_original_images(self):
        """Restore to original images"""
        try:
            restored_count = 0

            # Restore Image 1
            if self.image1_raw_original is not None:
                self.image1_raw = self.image1_raw_original.copy()
                # Regenerate 8-bit display image using fixed 16-bit range
                arr_display = (self.image1_raw.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                self.image1 = Image.fromarray(arr_display)
                self.panel1.set_image(self.image1)
                restored_count += 1

            # Restore Image 2
            if self.image2_raw_original is not None:
                self.image2_raw = self.image2_raw_original.copy()
                # Regenerate 8-bit display image using fixed 16-bit range
                arr_display = (self.image2_raw.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                self.image2 = Image.fromarray(arr_display)
                self.panel2.set_image(self.image2)
                restored_count += 1

            if restored_count > 0:
                self._calculate_diff()
                self._update_display()
                self.is_normalized = False
                self.norm_status_var.set("")
                self.norm_btn.configure(text="Normalize")
                self.status_var.set("Restored to original images")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore: {e}")

    def _normalize_single_image(self, image: Image.Image) -> Tuple[Optional[Image.Image], float]:
        """Normalize single image - set center 100x100 region average to target value"""
        try:
            # Convert image to numpy array
            arr = np.array(image, dtype=np.float32)

            # Calculate center 100x100 region
            h, w = arr.shape[:2]
            center_x, center_y = w // 2, h // 2
            half_size = 50

            x1 = max(0, center_x - half_size)
            x2 = min(w, center_x + half_size)
            y1 = max(0, center_y - half_size)
            y2 = min(h, center_y + half_size)

            # Convert to grayscale for average calculation
            if len(arr.shape) == 3:
                center_region = arr[y1:y2, x1:x2, 0]  # Use first channel
            else:
                center_region = arr[y1:y2, x1:x2]

            current_avg = np.mean(center_region)

            if current_avg == 0:
                messagebox.showwarning("Warning", "Center region average is 0, cannot normalize.")
                return None, 0.0

            # Convert current 8-bit image average to 16-bit scale for calculation
            # Convert average of 8-bit image to 16-bit scale
            current_avg_16bit = current_avg * 256  # 8-bit to 16-bit scale

            # Calculate normalization factor
            factor = self.NORMALIZATION_TARGET / current_avg_16bit

            # Factor for 8-bit basis
            factor_8bit = factor

            # Apply normalization
            normalized_arr = np.clip(arr * factor_8bit, 0, 255).astype(np.uint8)

            # Convert to PIL image
            if len(arr.shape) == 3:
                normalized_image = Image.fromarray(normalized_arr, mode='RGB')
            else:
                normalized_image = Image.fromarray(normalized_arr, mode='L')

            return normalized_image, factor

        except Exception as e:
            print(f"Normalization error: {e}")
            return None, 0.0

    def _save_images(self):
        """현재 이미지들을 파일로 저장"""
        if self.image1 is None and self.image2 is None:
            messagebox.showwarning("Warning", "No images to save.")
            return

        # 저장 폴더 선택
        save_dir = filedialog.askdirectory(title="Select folder to save images")
        if not save_dir:
            return

        import os
        saved_files = []

        try:
            # Image 1 저장 (16-bit TIFF) - 픽셀 값에 16을 곱함
            if self.image1_raw is not None:
                filepath1 = os.path.join(save_dir, "image1_normalized.tif")
                # 픽셀 값에 16을 곱하고 클리핑
                img1_scaled = np.clip(self.image1_raw.astype(np.uint32) * 16, 0, 65535).astype(np.uint16)
                img1_pil = Image.fromarray(img1_scaled)
                img1_pil.save(filepath1)
                saved_files.append("image1_normalized.tif")
            elif self.image1 is not None:
                filepath1 = os.path.join(save_dir, "image1.png")
                self.image1.save(filepath1)
                saved_files.append("image1.png")

            # Image 2 저장 (16-bit TIFF) - 픽셀 값에 16을 곱함
            if self.image2_raw is not None:
                filepath2 = os.path.join(save_dir, "image2_normalized.tif")
                # Multiply pixel values by 16 and clip
                img2_scaled = np.clip(self.image2_raw.astype(np.uint32) * 16, 0, 65535).astype(np.uint16)
                img2_pil = Image.fromarray(img2_scaled)
                img2_pil.save(filepath2)
                saved_files.append("image2_normalized.tif")
            elif self.image2 is not None:
                filepath2 = os.path.join(save_dir, "image2.png")
                self.image2.save(filepath2)
                saved_files.append("image2.png")

            # Save Diff image (16-bit TIFF) - diff_raw*16 + 30000, clip to 0~65535
            if self.diff_raw is not None:
                filepath_diff = os.path.join(save_dir, "diff_image.tif")
                # Formula: diff_raw * 16 + 30000, clip to range [0, 65535]
                diff_scaled = self.diff_raw.astype(np.float64) * 16 + 30000
                diff_clipped = np.clip(diff_scaled, 0, 65535).astype(np.uint16)
                diff_pil = Image.fromarray(diff_clipped)
                diff_pil.save(filepath_diff)
                saved_files.append("diff_image.tif")

                # Also save visualization diff image (RGB)
                if self.diff_image is not None:
                    filepath_diff_vis = os.path.join(save_dir, "diff_visualization.png")
                    self.diff_image.save(filepath_diff_vis)
                    saved_files.append("diff_visualization.png")

            if saved_files:
                self.status_var.set(f"Saved: {', '.join(saved_files)}")
                messagebox.showinfo("Save Complete",
                    f"Images saved to:\n{save_dir}\n\nFiles:\n" + "\n".join(saved_files))
            else:
                messagebox.showwarning("Warning", "No images were saved.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save images: {e}")

    def _go_to_center(self):
        """Move to image center"""
        if self.image_size[0] > 0:
            self.view_center_x = self.image_size[0] // 2
            self.view_center_y = self.image_size[1] // 2
            self.zoom_level = 1.0
            self._update_display()

    def _fit_to_window(self):
        """Adjust zoom to fit window"""
        if self.image_size[0] > 0:
            self.view_center_x = self.image_size[0] // 2
            self.view_center_y = self.image_size[1] // 2

            canvas_size = min(self.panel1.canvas.winfo_width(),
                            self.panel1.canvas.winfo_height()) - 20
            image_max = max(self.image_size)
            self.zoom_level = canvas_size / image_max
            self._update_display()

    def _zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.MAX_ZOOM, self.zoom_level + self.ZOOM_STEP)
        self._update_display()

    def _zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.MIN_ZOOM, self.zoom_level - self.ZOOM_STEP)
        self._update_display()

    def _on_mouse_wheel(self, event):
        """Mouse wheel event"""
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()

    def _on_drag_start(self, event):
        """Drag start"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        """Dragging"""
        if self.dragging and self.image_size[0] > 0:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y

            view_size = int(self.DEFAULT_VIEW_SIZE / self.zoom_level)
            scale = view_size / self._get_display_size()[0]

            self.view_center_x = max(0, min(self.image_size[0],
                                           self.view_center_x - int(dx * scale)))
            self.view_center_y = max(0, min(self.image_size[1],
                                           self.view_center_y - int(dy * scale)))

            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self._update_display()

    def _on_drag_end(self, event):
        """Drag end"""
        self.dragging = False

    def _on_click_release(self, event):
        """Click release - show pixel values if not dragging"""
        # Consider it a click if drag distance is short
        dx = abs(event.x - self.drag_start_x)
        dy = abs(event.y - self.drag_start_y)

        self.dragging = False

        # If click (not drag), show pixel values
        if dx < 5 and dy < 5:
            self._show_pixel_values(event)

    def _show_pixel_values(self, event):
        """Show pixel values of 3 images at clicked position (16-bit based)"""
        if self.image_size[0] == 0:
            return

        crop_box = self._get_crop_box()
        display_size = self._get_display_size()

        canvas_width = self.panel1.canvas.winfo_width()
        canvas_height = self.panel1.canvas.winfo_height()

        offset_x = (canvas_width - display_size[0]) // 2
        offset_y = (canvas_height - display_size[1]) // 2

        rel_x = event.x - offset_x
        rel_y = event.y - offset_y

        if 0 <= rel_x < display_size[0] and 0 <= rel_y < display_size[1]:
            # Calculate image coordinates
            img_x = int(crop_box[0] + rel_x * (crop_box[2] - crop_box[0]) / display_size[0])
            img_y = int(crop_box[1] + rel_y * (crop_box[3] - crop_box[1]) / display_size[1])

            # Get 16-bit pixel values from each image
            pixel_values = []

            # Image 1 pixel value (16-bit)
            if self.image1_raw is not None:
                try:
                    h, w = self.image1_raw.shape[:2]
                    if 0 <= img_x < w and 0 <= img_y < h:
                        pixel1 = self.image1_raw[img_y, img_x]
                        pixel_values.append(f"Img1: {pixel1}")
                    else:
                        pixel_values.append("Img1: -")
                except:
                    pixel_values.append("Img1: -")
            elif self.image1 is not None:
                try:
                    w, h = self.image1.size
                    if 0 <= img_x < w and 0 <= img_y < h:
                        pixel1 = self.image1.getpixel((img_x, img_y))
                        if isinstance(pixel1, tuple):
                            pixel1 = pixel1[0]
                        pixel_values.append(f"Img1: {pixel1 * 256}")  # 8-bit to 16-bit
                    else:
                        pixel_values.append("Img1: -")
                except:
                    pixel_values.append("Img1: -")
            else:
                pixel_values.append("Img1: -")

            # Image 2 pixel value (16-bit)
            if self.image2_raw is not None:
                try:
                    h, w = self.image2_raw.shape[:2]
                    if 0 <= img_x < w and 0 <= img_y < h:
                        pixel2 = self.image2_raw[img_y, img_x]
                        pixel_values.append(f"Img2: {pixel2}")
                    else:
                        pixel_values.append("Img2: -")
                except:
                    pixel_values.append("Img2: -")
            elif self.image2 is not None:
                try:
                    w, h = self.image2.size
                    if 0 <= img_x < w and 0 <= img_y < h:
                        pixel2 = self.image2.getpixel((img_x, img_y))
                        if isinstance(pixel2, tuple):
                            pixel2 = pixel2[0]
                        pixel_values.append(f"Img2: {pixel2 * 256}")  # 8-bit to 16-bit
                    else:
                        pixel_values.append("Img2: -")
                except:
                    pixel_values.append("Img2: -")
            else:
                pixel_values.append("Img2: -")

            # Difference value (actual difference: img1 - img2)
            if self.diff_raw is not None:
                try:
                    h, w = self.diff_raw.shape[:2]
                    if 0 <= img_x < w and 0 <= img_y < h:
                        diff_val = self.diff_raw[img_y, img_x]
                        pixel_values.append(f"Diff: {diff_val:.0f}")
                    else:
                        pixel_values.append("Diff: -")
                except:
                    pixel_values.append("Diff: -")
            else:
                pixel_values.append("Diff: -")

            # Display pixel info
            info_text = f"({img_x}, {img_y})  |  " + "  |  ".join(pixel_values)
            self.pixel_info_var.set(info_text)

            # Save clicked position and show marker
            self.clicked_pixel_x = img_x
            self.clicked_pixel_y = img_y
            self._show_markers(img_x, img_y)

    def _show_markers(self, img_x: int, img_y: int):
        """Show markers on all 3 image panels"""
        crop_box = self._get_crop_box()
        display_size = self._get_display_size()

        self.panel1.show_marker(img_x, img_y, crop_box, display_size)
        self.panel2.show_marker(img_x, img_y, crop_box, display_size)
        self.panel_diff.show_marker(img_x, img_y, crop_box, display_size)

    def _on_mouse_move(self, event):
        """Mouse move"""
        if self.image_size[0] > 0:
            crop_box = self._get_crop_box()
            display_size = self._get_display_size()

            canvas_width = self.panel1.canvas.winfo_width()
            canvas_height = self.panel1.canvas.winfo_height()

            offset_x = (canvas_width - display_size[0]) // 2
            offset_y = (canvas_height - display_size[1]) // 2

            rel_x = event.x - offset_x
            rel_y = event.y - offset_y

            if 0 <= rel_x < display_size[0] and 0 <= rel_y < display_size[1]:
                img_x = int(crop_box[0] + rel_x * (crop_box[2] - crop_box[0]) / display_size[0])
                img_y = int(crop_box[1] + rel_y * (crop_box[3] - crop_box[1]) / display_size[1])
                self.position_var.set(f"Position: ({img_x}, {img_y})")
            else:
                self.position_var.set("")

    def _on_resize(self, event):
        """Window resize"""
        self._update_display()

    def run(self):
        """Run application"""
        self.root.mainloop()


def main():
    """Main function"""
    root = tk.Tk()
    app = ImageCompareApp(root)
    app.run()


if __name__ == "__main__":
    main()
