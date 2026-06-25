# step12.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

cv2.imwrite("mask_closed.jpg", closed)
print("mask_closed.jpg を保存しました。穴が埋まったか確認してください。")
