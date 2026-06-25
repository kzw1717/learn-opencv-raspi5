# step16.py
import cv2

leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print("見つかった輪郭の数:", len(contours))
