# step18.py
import cv2
import numpy as np

mat = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
contours, _ = cv2.findContours(mat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 十分大きい断片だけ集める（小さなゴミは無視）
MIN_MAT_FRAGMENT = 2000
pts = [c for c in contours if cv2.contourArea(c) >= MIN_MAT_FRAGMENT]

# 断片の点を全部まとめて、外側を輪ゴムで囲う＝凸包
hull = cv2.convexHull(np.vstack(pts))

print("断片の数:", len(pts))
print("凸包の頂点の数:", len(hull))
