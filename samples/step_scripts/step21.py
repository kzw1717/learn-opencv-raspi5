# step21.py
import cv2

region = cv2.imread("mat_region.jpg", cv2.IMREAD_GRAYSCALE)
leaf   = cv2.imread("leaf.jpg",       cv2.IMREAD_GRAYSCALE)

region_area = cv2.countNonZero(region)
leaf_area   = cv2.countNonZero(leaf)

coverage_pct = 100.0 * leaf_area / region_area if region_area else 0.0
print(f"被覆面積率 = {coverage_pct:.2f}%")
