# Architecture Documentation

## Overview

This project contains two GUI applications for image analysis and comparison, built with PyQt5 and Python. Both applications are designed for display hardware calibration workflows, supporting 16-bit TIFF images and CSV profile data.

---

## System Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        M1["src/main.py<br/>(Image Compare Tool)"]
        M2["gui/main_window.py<br/>(Image Analysis GUI)"]
    end

    subgraph "Image Compare Tool"
        ICA["ImageCompareApp<br/>(QMainWindow)"]
        IP["ImagePanel<br/>(QGroupBox)"]
        IC["ImageCanvas<br/>(QWidget)"]
        TH["Theme<br/>(Styling)"]
    end

    subgraph "Image Analysis GUI"
        MW["MainWindow<br/>(QMainWindow)"]
        IV["ImageViewer<br/>(QWidget)"]
        CP["ControlPanel<br/>(QWidget)"]
        IPR["ImageProcessor<br/>(Core Engine)"]
    end

    subgraph "Utilities"
        H["helpers.py<br/>(Image Utils)"]
    end

    subgraph "Legacy"
        TK["src/etc/image_compare_app.py<br/>(Tkinter version)"]
    end

    M1 --> ICA
    ICA --> IP
    IP --> IC
    ICA --> TH

    M2 --> MW
    MW --> IV
    MW --> CP
    MW --> IPR
    CP -->|"process_requested<br/>signal"| MW
    MW -->|"process()"| IPR

    MW --> H

    style M1 fill:#6c9bce,color:#fff
    style M2 fill:#6c9bce,color:#fff
    style TK fill:#888,color:#fff
```

---

## Application 1: Image Compare Tool

The primary application for comparing two images side-by-side with pixel-level difference visualization. Optimized for 16-bit display calibration images.

### Class Diagram

```mermaid
classDiagram
    class ImageCompareApp {
        -image1: Image
        -image2: Image
        -diff_image: Image
        -image1_raw: ndarray[uint16]
        -image2_raw: ndarray[uint16]
        -diff_raw: ndarray[float32]
        -zoom_level: float
        -view_center_x: int
        -view_center_y: int
        -is_normalized: bool
        +DEFAULT_VIEW_SIZE = 100
        +NORMALIZATION_TARGET = 30000
        -_load_image1()
        -_load_image2()
        -_load_image(filepath, store_raw)
        -_load_csv_as_image(filepath)
        -_calculate_diff()
        -_normalize_images()
        -_restore_original_images()
        -_save_images()
        -_update_display()
        -_show_pixel_values(x, y)
    }

    class ImagePanel {
        -base_title: str
        -canvas: ImageCanvas
        -image: Image
        -size_label: QLabel
        -view_label: QLabel
        +set_image(image, filename)
        +display(crop_box, display_size)
        +show_marker(img_x, img_y, crop_box, display_size)
        +clear_marker()
    }

    class ImageCanvas {
        -_pixmap: QPixmap
        -_marker_pos: tuple
        -_drag_active: bool
        <<signals>>
        +dragged(dx, dy)
        +drag_started(x, y)
        +drag_released(x, y, sx, sy)
        +mouse_moved(x, y)
        +wheel_scrolled(delta)
        +set_pixmap(pixmap)
        +set_marker(cx, cy)
        +paintEvent(event)
    }

    class Theme {
        +BG_PRIMARY: str
        +BG_SECONDARY: str
        +ACCENT: str
        +CANVAS_BG: str
        +MARKER_COLOR: str
    }

    ImageCompareApp "1" *-- "3" ImagePanel : panel1, panel2, panel_diff
    ImagePanel "1" *-- "1" ImageCanvas
    ImageCompareApp ..> Theme
```

### Data Flow

```mermaid
flowchart LR
    subgraph Input
        TIF["16-bit TIFF"]
        CSV["CSV Profile"]
        PNG["8-bit PNG/JPG"]
    end

    subgraph Loading
        LI["_load_image()"]
        LC["_load_csv_as_image()"]
    end

    subgraph Storage
        RAW["raw: uint16 array<br/>(16-bit original)"]
        IMG["image: PIL Image<br/>(8-bit display)"]
    end

    subgraph Processing
        NORM["Normalize<br/>(center 100×100 avg → 30000)"]
        DIFF["Calculate Diff<br/>(img1_raw - img2_raw)"]
    end

    subgraph Display
        P1["Panel 1<br/>(Image 1)"]
        P2["Panel 2<br/>(Image 2)"]
        PD["Panel Diff<br/>(Heatmap)"]
        PIX["Pixel Info Bar<br/>(16-bit values)"]
    end

    TIF --> LI
    CSV --> LC
    PNG --> LI
    LC --> LI

    LI --> RAW
    LI --> IMG

    RAW --> NORM
    NORM --> DIFF
    RAW --> DIFF

    IMG --> P1
    IMG --> P2
    DIFF --> PD
    RAW --> PIX
```

### Image Loading Pipeline

```mermaid
flowchart TD
    A["Load File"] --> B{File Extension?}

    B -->|".csv"| C["Parse CSV<br/>detect delimiter<br/>skip headers"]
    B -->|".tif"| D["PIL.Image.open()"]
    B -->|".png/.jpg"| E["PIL.Image.open()"]

    C --> F["numpy array<br/>(float64)"]
    F --> G["Normalize to uint16<br/>(0-65535)"]

    D --> H{Image Mode?}
    H -->|"I;16"| I["Read as uint16"]
    H -->|"I"| J["Read as int32<br/>clip to 0-65535"]
    H -->|"RGB/L"| K["Read as uint8<br/>scale ×256"]

    E --> H

    G --> L["Store as raw<br/>(uint16)"]
    I --> L
    J --> L
    K --> L

    G --> M["Convert to 8-bit<br/>for display"]
    I --> M
    J --> M
    K --> N["Use as-is<br/>for display"]

    L --> O["Ready for<br/>16-bit operations"]
    M --> P["Ready for<br/>GUI display"]
    N --> P
```

### Synchronized View System

```mermaid
flowchart TD
    subgraph "View State (shared)"
        VC["view_center_x, view_center_y"]
        ZL["zoom_level"]
        CB["crop_box = f(center, zoom)"]
    end

    subgraph "User Input"
        MW["Mouse Wheel → zoom"]
        DR["Drag → pan"]
        CL["Click → pixel info"]
        BTN["Buttons: Center, Fit, +, -"]
    end

    subgraph "Synchronized Panels"
        P1["Panel 1"]
        P2["Panel 2"]
        PD["Panel Diff"]
    end

    MW --> ZL
    DR --> VC
    BTN --> VC
    BTN --> ZL

    VC --> CB
    ZL --> CB

    CB --> P1
    CB --> P2
    CB --> PD

    CL -->|"same coords"| P1
    CL -->|"same coords"| P2
    CL -->|"same coords"| PD
```

### Difference Visualization

```mermaid
flowchart LR
    subgraph "Input"
        R1["Image 1 Raw<br/>(uint16)"]
        R2["Image 2 Raw<br/>(uint16)"]
    end

    DIFF["diff = img1 - img2<br/>(float32, signed)"]

    R1 --> DIFF
    R2 --> DIFF

    subgraph "Color Mapping"
        POS["diff ≥ 0<br/>→ Green channel"]
        NEG["diff < 0<br/>→ Red channel"]
    end

    DIFF --> POS
    DIFF --> NEG

    subgraph "Output"
        RGB["RGB Heatmap<br/>Green = img1 brighter<br/>Red = img2 brighter<br/>Black = equal"]
    end

    POS --> RGB
    NEG --> RGB
```

---

## Application 2: Image Analysis GUI

A general-purpose image analysis tool with OpenCV-based processing operations.

### Class Diagram

```mermaid
classDiagram
    class MainWindow {
        -image_processor: ImageProcessor
        -current_image: ndarray
        -image_viewer: ImageViewer
        -control_panel: ControlPanel
        +open_image()
        +save_image()
        +process_image(operation, params)
        +show_histogram()
        +show_statistics()
    }

    class ImageViewer {
        -current_pixmap: QPixmap
        -zoom_factor: float
        <<signals>>
        +zoom_changed(float)
        +set_image(ndarray)
        +zoom_in()
        +zoom_out()
        +fit_to_window()
    }

    class ControlPanel {
        <<signals>>
        +process_requested(str, dict)
        -_create_basic_tab()
        -_create_filters_tab()
        -_create_analysis_tab()
    }

    class ImageProcessor {
        +load_image(path): ndarray
        +save_image(ndarray, path): bool
        +process(ndarray, op, params): ndarray
        -_brightness_contrast()
        -_rotate()
        -_flip()
        -_resize()
        -_blur()
        -_edge_detection()
        -_threshold()
        -_morphology()
        -_color_convert()
        -_histogram_equalization()
        +show_histogram(ndarray)
        +get_statistics(ndarray): dict
    }

    MainWindow *-- ImageViewer
    MainWindow *-- ControlPanel
    MainWindow *-- ImageProcessor
    ControlPanel ..> MainWindow : process_requested signal
```

### Processing Pipeline

```mermaid
flowchart LR
    subgraph "Control Panel Tabs"
        BT["Basic<br/>• Brightness/Contrast<br/>• Rotate/Flip<br/>• Resize"]
        FT["Filters<br/>• Blur (Gaussian/Avg/Median)<br/>• Edge (Canny/Sobel/Laplacian)<br/>• Threshold<br/>• Morphology"]
        AT["Analysis<br/>• Histogram<br/>• Color Space<br/>• Statistics<br/>• Contours"]
    end

    SIG["process_requested<br/>signal(op, params)"]

    BT --> SIG
    FT --> SIG
    AT --> SIG

    IP["ImageProcessor.process()"]
    SIG --> IP

    IV["ImageViewer<br/>display result"]
    IP --> IV
```

---

## Project Structure

```mermaid
graph TD
    subgraph "Root"
        README["README.md"]
        REQ["requirements.txt"]
        TEST["test_app.py"]
        BAT["build_exe.bat"]
        GIT[".gitignore"]
    end

    subgraph "src/ — Image Compare Tool"
        MAIN["main.py<br/>(entry point)"]
        APP["image_compare_app_pyqt5.py<br/>(PyQt5 - current)"]
        subgraph "src/etc/ — Legacy"
            LEGACY["image_compare_app.py<br/>(Tkinter - original)"]
        end
    end

    subgraph "gui/ — Image Analysis GUI"
        GMW["main_window.py"]
        GIV["image_viewer.py"]
        GCP["control_panel.py"]
    end

    subgraph "core/"
        CIP["image_processor.py<br/>(OpenCV operations)"]
    end

    subgraph "utils/"
        UH["helpers.py"]
    end

    subgraph "data/"
        DR["DATA_README.md"]
        TIFS["*.tif (calibration images)"]
        CSVS["*.csv (profile data)"]
        subgraph "data/test/"
            TI["test images (PNG)"]
            CTS["create_test_images.py"]
        end
    end

    subgraph "docs/"
        UM["USER_MANUAL.md"]
        PPT["*.pptx (presentations)"]
        SS["screenshots/"]
    end

    MAIN --> APP
    GMW --> GIV
    GMW --> GCP
    GMW --> CIP
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **GUI Framework** | PyQt5 | Window management, widgets, event handling |
| **Image I/O** | Pillow (PIL) | Load/save images (TIFF, PNG, JPG, BMP) |
| **Image Processing** | OpenCV | Filters, edge detection, morphology, color conversion |
| **Numerical** | NumPy | Array operations, 16-bit math, normalization |
| **Visualization** | Matplotlib | Histogram display |
| **Legacy GUI** | Tkinter | Original Compare Tool (preserved in `src/etc/`) |

## Key Design Decisions

1. **Dual raw/display storage**: Images are stored as both 16-bit raw (`uint16` ndarray) and 8-bit display (`PIL.Image`). This preserves precision for pixel-level analysis while enabling GUI rendering.

2. **Synchronized 3-panel view**: All three panels (Image 1, Image 2, Difference) share the same `view_center`, `zoom_level`, and `crop_box`. Any zoom/pan applies to all panels simultaneously.

3. **Green/Red difference heatmap**: Positive differences (img1 > img2) map to green; negative (img1 < img2) map to red. This provides intuitive visual distinction of over/under-exposure.

4. **Center-region normalization**: Normalization targets the center 100×100 pixel region average to a fixed value (30000 in 16-bit scale), making calibration comparisons consistent regardless of absolute brightness.

5. **Fixed 65535 scaling**: 16-bit to 8-bit conversion always divides by 65535 (not by the image's max value), ensuring consistent brightness representation across images with different dynamic ranges.
