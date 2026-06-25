# step20.py
import cv2

region = cv2.imread("mat_region.jpg", cv2.IMREAD_GRAYSCALE)   # 第6章で作ったマット外形
leaf   = cv2.imread("leaf.jpg",       cv2.IMREAD_GRAYSCALE)   # 第5章で作った堆積物

region_area = cv2.countNonZero(region)
leaf_area   = cv2.countNonZero(leaf)

print("計測範囲の面積:", region_area, "px")
print("堆積物の面積  :", leaf_area,   "px")
