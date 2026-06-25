# step23.py
import cv2

img  = cv2.imread("mat.jpg")
leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)
region = cv2.imread("mat_region.jpg", cv2.IMREAD_GRAYSCALE)

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clumps = [c for c in contours if cv2.contourArea(c) >= 600]

region_area = cv2.countNonZero(region)
leaf_area   = cv2.countNonZero(leaf)
coverage = 100.0 * leaf_area / region_area if region_area else 0.0

annotated = img.copy()
cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)   # 堆積物：緑

label = f"coverage={coverage:.2f}%  clumps={len(clumps)}"
cv2.putText(annotated, label, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)   # 赤い文字

cv2.imwrite("annotated_full.jpg", annotated)
print("annotated_full.jpg を保存しました。左上に数値が出ているか確認してください。")
