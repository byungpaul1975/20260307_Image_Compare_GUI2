"""
테스트용 샘플 이미지 생성 스크립트
"""

import numpy as np
from PIL import Image
import os

def create_test_images():
    """테스트용 샘플 이미지 생성"""

    data_dir = os.path.dirname(os.path.abspath(__file__))

    # 이미지 크기
    width, height = 256, 256

    # 1. 그라디언트 이미지 (기준 이미지)
    gradient = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            gradient[y, x] = int((x + y) / 2)

    img_gradient = Image.fromarray(gradient, mode='L')
    img_gradient.save(os.path.join(data_dir, 'test_image_A.png'))
    print("Created: test_image_A.png (gradient)")

    # 2. 그라디언트 + 노이즈 (약간 다른 이미지)
    noise = np.random.randint(-20, 20, (height, width), dtype=np.int16)
    gradient_noisy = np.clip(gradient.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    img_noisy = Image.fromarray(gradient_noisy, mode='L')
    img_noisy.save(os.path.join(data_dir, 'test_image_B.png'))
    print("Created: test_image_B.png (gradient + noise)")

    # 3. 원형 패턴 이미지
    circle = np.zeros((height, width), dtype=np.uint8)
    center_x, center_y = width // 2, height // 2
    for y in range(height):
        for x in range(width):
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            circle[y, x] = int(255 * (1 - min(dist / 100, 1)))

    img_circle = Image.fromarray(circle, mode='L')
    img_circle.save(os.path.join(data_dir, 'test_circle_A.png'))
    print("Created: test_circle_A.png (circle pattern)")

    # 4. 원형 패턴 + 오프셋 (위치 이동)
    circle_offset = np.zeros((height, width), dtype=np.uint8)
    offset_x, offset_y = 10, 10
    for y in range(height):
        for x in range(width):
            dist = np.sqrt((x - center_x - offset_x)**2 + (y - center_y - offset_y)**2)
            circle_offset[y, x] = int(255 * (1 - min(dist / 100, 1)))

    img_circle_offset = Image.fromarray(circle_offset, mode='L')
    img_circle_offset.save(os.path.join(data_dir, 'test_circle_B.png'))
    print("Created: test_circle_B.png (circle pattern with offset)")

    # 5. 체커보드 패턴
    checker = np.zeros((height, width), dtype=np.uint8)
    block_size = 32
    for y in range(height):
        for x in range(width):
            if ((x // block_size) + (y // block_size)) % 2 == 0:
                checker[y, x] = 200
            else:
                checker[y, x] = 50

    img_checker = Image.fromarray(checker, mode='L')
    img_checker.save(os.path.join(data_dir, 'test_checker_A.png'))
    print("Created: test_checker_A.png (checkerboard)")

    # 6. 체커보드 + 밝기 변화
    checker_bright = np.clip(checker.astype(np.int16) + 30, 0, 255).astype(np.uint8)

    img_checker_bright = Image.fromarray(checker_bright, mode='L')
    img_checker_bright.save(os.path.join(data_dir, 'test_checker_B.png'))
    print("Created: test_checker_B.png (checkerboard brighter)")

    # 7. RGB 컬러 이미지
    color_img = np.zeros((height, width, 3), dtype=np.uint8)
    color_img[:, :, 0] = gradient  # Red channel
    color_img[:, :, 1] = 255 - gradient  # Green channel
    color_img[:, :, 2] = 128  # Blue channel

    img_color = Image.fromarray(color_img, mode='RGB')
    img_color.save(os.path.join(data_dir, 'test_color_A.png'))
    print("Created: test_color_A.png (RGB gradient)")

    # 8. RGB 컬러 이미지 변형
    color_img2 = np.zeros((height, width, 3), dtype=np.uint8)
    color_img2[:, :, 0] = 255 - gradient  # Red channel swapped
    color_img2[:, :, 1] = gradient  # Green channel swapped
    color_img2[:, :, 2] = 128  # Blue channel same

    img_color2 = Image.fromarray(color_img2, mode='RGB')
    img_color2.save(os.path.join(data_dir, 'test_color_B.png'))
    print("Created: test_color_B.png (RGB gradient inverted)")

    print("\n모든 테스트 이미지가 생성되었습니다.")
    print(f"위치: {data_dir}")


if __name__ == "__main__":
    create_test_images()
