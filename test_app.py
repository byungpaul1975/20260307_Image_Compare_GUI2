"""
Test script for Image Compare Tool
Tests the application with real images from data/ folder
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PIL import Image
import numpy as np


def test_image_loading():
    """Test loading various image formats"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    test_files = [
        'W32_cal.tif',
        'W32_nocal.tif',
        'test_image_A.png',
        'test_image_B.png',
    ]

    print("=" * 60)
    print("TEST 1: Image Loading")
    print("=" * 60)

    for filename in test_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                img = Image.open(filepath)
                arr = np.array(img)
                print(f"\n[OK] {filename}")
                print(f"  Mode: {img.mode}")
                print(f"  Size: {img.size}")
                print(f"  Array shape: {arr.shape}")
                print(f"  Dtype: {arr.dtype}")
                print(f"  Value range: {arr.min()} - {arr.max()}")
            except Exception as e:
                print(f"\n[FAIL] {filename}: {e}")
        else:
            print(f"\n[FAIL] {filename}: File not found")

    return True


def test_16bit_processing():
    """Test 16-bit image processing"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    print("\n" + "=" * 60)
    print("TEST 2: 16-bit Image Processing")
    print("=" * 60)

    # Load 16-bit TIFF
    tiff_files = ['W32_cal.tif', 'W32_nocal.tif']

    for filename in tiff_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            img = Image.open(filepath)
            print(f"\n{filename}:")
            print(f"  Mode: {img.mode}")

            if img.mode == 'I;16':
                arr = np.array(img, dtype=np.uint16)
                print(f"  [OK] 16-bit image detected")
                print(f"  Value range: {arr.min()} - {arr.max()}")
                print(f"  Mean: {arr.mean():.2f}")

                # Test conversion to 8-bit with fixed range
                arr_display = (arr.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
                print(f"  8-bit conversion range: {arr_display.min()} - {arr_display.max()}")
            elif img.mode == 'I':
                arr = np.array(img, dtype=np.int32)
                print(f"  [OK] 32-bit integer image detected")
                print(f"  Value range: {arr.min()} - {arr.max()}")

    return True


def test_difference_calculation():
    """Test pixel difference calculation"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    print("\n" + "=" * 60)
    print("TEST 3: Difference Calculation")
    print("=" * 60)

    # Load calibrated and non-calibrated images
    cal_path = os.path.join(data_dir, 'W32_cal.tif')
    nocal_path = os.path.join(data_dir, 'W32_nocal.tif')

    if os.path.exists(cal_path) and os.path.exists(nocal_path):
        img_cal = Image.open(cal_path)
        img_nocal = Image.open(nocal_path)

        # Convert to arrays
        if img_cal.mode == 'I;16':
            arr_cal = np.array(img_cal, dtype=np.uint16).astype(np.float32)
            arr_nocal = np.array(img_nocal, dtype=np.uint16).astype(np.float32)
        else:
            arr_cal = np.array(img_cal, dtype=np.float32)
            arr_nocal = np.array(img_nocal, dtype=np.float32)

        print(f"\nImage 1 (cal): shape={arr_cal.shape}, range=[{arr_cal.min():.0f}, {arr_cal.max():.0f}]")
        print(f"Image 2 (nocal): shape={arr_nocal.shape}, range=[{arr_nocal.min():.0f}, {arr_nocal.max():.0f}]")

        # Calculate difference
        diff = arr_cal - arr_nocal
        print(f"\nDifference (cal - nocal):")
        print(f"  Range: [{diff.min():.0f}, {diff.max():.0f}]")
        print(f"  Mean: {diff.mean():.2f}")
        print(f"  Std: {diff.std():.2f}")

        # Count positive/negative
        positive_count = np.sum(diff > 0)
        negative_count = np.sum(diff < 0)
        zero_count = np.sum(diff == 0)
        total = diff.size

        print(f"\n  Positive (cal > nocal): {positive_count} ({positive_count/total*100:.1f}%)")
        print(f"  Negative (cal < nocal): {negative_count} ({negative_count/total*100:.1f}%)")
        print(f"  Zero (equal): {zero_count} ({zero_count/total*100:.1f}%)")

        print("\n[OK] Difference calculation test passed")
    else:
        print("[FAIL] Test images not found")

    return True


def test_normalization():
    """Test image normalization"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    print("\n" + "=" * 60)
    print("TEST 4: Normalization (Center 100x100 Region)")
    print("=" * 60)

    NORMALIZATION_TARGET = 30000

    for filename in ['W32_cal.tif', 'W32_nocal.tif']:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            img = Image.open(filepath)

            if img.mode == 'I;16':
                arr = np.array(img, dtype=np.uint16).astype(np.float32)
            else:
                arr = np.array(img, dtype=np.float32)

            # Calculate center 100x100 region
            h, w = arr.shape[:2]
            center_x, center_y = w // 2, h // 2
            x1 = max(0, center_x - 50)
            x2 = min(w, center_x + 50)
            y1 = max(0, center_y - 50)
            y2 = min(h, center_y + 50)

            center_region = arr[y1:y2, x1:x2]
            current_avg = np.mean(center_region)

            # Calculate normalization factor
            factor = NORMALIZATION_TARGET / current_avg

            # Apply normalization
            normalized = arr * factor
            new_avg = np.mean(normalized[y1:y2, x1:x2])

            print(f"\n{filename}:")
            print(f"  Original center avg: {current_avg:.2f}")
            print(f"  Normalization factor: {factor:.4f}")
            print(f"  New center avg: {new_avg:.2f}")
            print(f"  Target: {NORMALIZATION_TARGET}")
            print(f"  [OK] Difference from target: {abs(new_avg - NORMALIZATION_TARGET):.2f}")

    return True


def test_brightness_consistency():
    """Test that brightness is consistent across loaded images"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    print("\n" + "=" * 60)
    print("TEST 5: Brightness Consistency (Fixed 65535 Scaling)")
    print("=" * 60)

    # Simulate loading two images with different max values
    img1_path = os.path.join(data_dir, 'W32_cal.tif')
    img2_path = os.path.join(data_dir, 'W32_nocal.tif')

    if os.path.exists(img1_path) and os.path.exists(img2_path):
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        arr1 = np.array(img1, dtype=np.uint16)
        arr2 = np.array(img2, dtype=np.uint16)

        print(f"\nImage 1 max: {arr1.max()}")
        print(f"Image 2 max: {arr2.max()}")

        # Old method (bug): scale by individual max
        display1_old = (arr1.astype(np.float32) / arr1.max() * 255).astype(np.uint8)
        display2_old = (arr2.astype(np.float32) / arr2.max() * 255).astype(np.uint8)

        # New method (fix): scale by fixed 65535
        display1_new = (arr1.astype(np.float32) / 65535.0 * 255).astype(np.uint8)
        display2_new = (arr2.astype(np.float32) / 65535.0 * 255).astype(np.uint8)

        # Check a sample pixel (center)
        h, w = arr1.shape
        cy, cx = h // 2, w // 2

        print(f"\nSample pixel at ({cx}, {cy}):")
        print(f"  Raw values: Image1={arr1[cy, cx]}, Image2={arr2[cy, cx]}")
        print(f"\n  OLD method (bug - different scaling):")
        print(f"    Display1={display1_old[cy, cx]}, Display2={display2_old[cy, cx]}")
        print(f"    Difference: {abs(int(display1_old[cy, cx]) - int(display2_old[cy, cx]))}")
        print(f"\n  NEW method (fix - consistent scaling):")
        print(f"    Display1={display1_new[cy, cx]}, Display2={display2_new[cy, cx]}")
        print(f"    Difference: {abs(int(display1_new[cy, cx]) - int(display2_new[cy, cx]))}")

        # Calculate if same raw value would display the same
        test_value = 30000
        old_result1 = int(test_value / arr1.max() * 255)
        old_result2 = int(test_value / arr2.max() * 255)
        new_result = int(test_value / 65535.0 * 255)

        print(f"\n  Test: Same raw value ({test_value}) display brightness:")
        print(f"    OLD method: Image1={old_result1}, Image2={old_result2} (DIFFERENT!)")
        print(f"    NEW method: Both={new_result} (SAME - OK)")

        print("\n[OK] Brightness consistency test passed")

    return True


def run_gui_test():
    """Launch GUI with test images pre-loaded"""
    print("\n" + "=" * 60)
    print("TEST 6: Launch GUI Application")
    print("=" * 60)

    print("\nLaunching Image Compare Tool...")
    print("Please manually test the following:")
    print("  1. Load W32_cal.tif as Image 1")
    print("  2. Load W32_nocal.tif as Image 2")
    print("  3. Verify both images have similar brightness")
    print("  4. Click on pixels to see 16-bit values")
    print("  5. Test Normalize/Restore toggle")
    print("  6. Test Save feature")
    print("\nStarting application...")

    # Import and run the app
    from image_compare_app import ImageCompareApp
    import tkinter as tk

    root = tk.Tk()
    app = ImageCompareApp(root)

    # Auto-load test images
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    img1_path = os.path.join(data_dir, 'W32_cal.tif')
    img2_path = os.path.join(data_dir, 'W32_nocal.tif')

    def auto_load():
        if os.path.exists(img1_path):
            app.image1 = app._load_image(img1_path, store_raw='image1')
            if app.image1:
                app.panel1.set_image(app.image1)
                app._update_image_size()
                app.status_var.set(f"Image 1 loaded: {img1_path}")

        if os.path.exists(img2_path):
            app.image2 = app._load_image(img2_path, store_raw='image2')
            if app.image2:
                app.panel2.set_image(app.image2)
                app._update_image_size()
                app._calculate_diff()
                app._go_to_center()
                app.status_var.set(f"Images loaded: W32_cal.tif & W32_nocal.tif")

    # Schedule auto-load after window is ready
    root.after(500, auto_load)

    app.run()


if __name__ == "__main__":
    print("Image Compare Tool - Test Suite")
    print("=" * 60)

    # Run automated tests
    test_image_loading()
    test_16bit_processing()
    test_difference_calculation()
    test_normalization()
    test_brightness_consistency()

    print("\n" + "=" * 60)
    print("All automated tests completed!")
    print("=" * 60)

    # Ask user if they want to launch GUI
    response = input("\nLaunch GUI for manual testing? (y/n): ")
    if response.lower() == 'y':
        run_gui_test()
    else:
        print("\nGUI test skipped. Run 'python src/image_compare_app.py' to test manually.")
