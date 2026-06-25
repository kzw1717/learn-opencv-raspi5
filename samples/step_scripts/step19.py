# step19.py
import cv2
import numpy as np

mat = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
contours, _ = cv2.findContours(mat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
pts = [c for c in contours if cv2.contourArea(c) >= 2000]
hull = cv2.convexHull(np.vstack(pts))

# 真っ黒な画像を用意し、凸包の内部を白(255)で塗る
region = np.zeros(mat.shape, dtype=np.uint8)
cv2.fillPoly(region, [hull], 255)

cv2.imwrite("mat_region.jpg", region)
print("mat_region.jpg を保存しました。マット全体が白い1枚の領域になっているか確認してください。")
