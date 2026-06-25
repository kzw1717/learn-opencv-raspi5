# step11.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)   # マスクは白黒で読む
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

cv2.imwrite("mask_opened.jpg", opened)
print("mask_opened.jpg を保存しました。元の mat_mask.jpg と見比べてください。")
