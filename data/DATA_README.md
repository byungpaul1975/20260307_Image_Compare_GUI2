# Data Folder - Git Exclusion Notice

## Why are data files excluded from Git?

The `data/` folder contains large image and CSV files that exceed GitHub's **100MB per-file limit**. These files are excluded via `.gitignore` to keep the repository manageable.

**Total local size: ~2.46 GB**

## Excluded Files

### TIFF Images (`.tif`) — Calibration Data

| File | Size | Description |
|------|------|-------------|
| `B32_cal.tif` | 183 MB | Blue channel, 32-bit, calibrated |
| `B32_nocal.tif` | 222 MB | Blue channel, 32-bit, non-calibrated |
| `G32_cal.tif` | 202 MB | Green channel, 32-bit, calibrated |
| `G32_nocal.tif` | 236 MB | Green channel, 32-bit, non-calibrated |
| `R32_cal.tif` | 185 MB | Red channel, 32-bit, calibrated |
| `R32_nocal.tif` | 225 MB | Red channel, 32-bit, non-calibrated |
| `W32.tif` | 207 MB | White channel, 32-bit |
| `W32_cal.tif` | 195 MB | White channel, 32-bit, calibrated |
| `W32_nocal.tif` | 208 MB | White channel, 32-bit, non-calibrated |
| `image1.tif` | 301 MB | Sample analysis image |

### CSV Files (`.csv`) — Profile Data

| File | Size | Description |
|------|------|-------------|
| `Blue128.csv` | 33 MB | Blue channel, 128-level profile |
| `Blue32.csv` | 33 MB | Blue channel, 32-level profile |
| `Green128.csv` | 34 MB | Green channel, 128-level profile |
| `Green32.csv` | 33 MB | Green channel, 32-level profile |
| `Red128.csv` | 33 MB | Red channel, 128-level profile |
| `Red32.csv` | 33 MB | Red channel, 32-level profile |
| `W128.csv` | 38 MB | White channel, 128-level profile |
| `W32.csv` | 33 MB | White channel, 32-level profile |

### PNG Images (`.png`) — Capture Snapshots

| File | Size | Description |
|------|------|-------------|
| `P1S1-1_B32_*.png` | 6 MB | Blue 32-level capture |
| `P1S1-1_G64_*.png` | 6 MB | Green 64-level capture |
| `P1S1-1_R32_*.png` | 5 MB | Red 32-level capture |
| `P1S1-1_W128_*.png` | 6 MB | White 128-level capture |
| `P1S1-1_W64_*.png` | 6 MB | White 64-level capture |

## Included in Git

The `data/test/` subfolder **is tracked** in Git. It contains small test images used for automated testing:

- `test_image_A.png`, `test_image_B.png` — Gradient test pair
- `test_circle_A.png`, `test_circle_B.png` — Circle position test pair
- `test_checker_A.png`, `test_checker_B.png` — Checkerboard brightness test pair
- `test_color_A.png`, `test_color_B.png` — Color channel test pair
- `create_test_images.py` — Script to regenerate test images
- `plotProfile.PNG` — Reference screenshot

## How to Get the Data Files

After cloning the repository, obtain the data files separately:

1. **From the original source**: Copy the `data/` folder contents from the project owner
2. **Generate test data**: Run `python data/test/create_test_images.py` to create test images

## .gitignore Rules

The following rules in `.gitignore` control data file exclusions:

```gitignore
# Large data files (exceed GitHub 100MB limit)
data/*.tif
data/*.csv
data/*.png
!data/test/
```

- `data/*.tif` — Excludes all TIFF files in `data/`
- `data/*.csv` — Excludes all CSV files in `data/`
- `data/*.png` — Excludes all PNG files directly in `data/` (not subdirectories)
- `!data/test/` — Re-includes the `data/test/` subfolder
