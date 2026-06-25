# step13.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

dilated = cv2.dilate(mask, kernel, iterations=1)

cv2.imwrite("mask_dilated.jpg", dilated)
print("mask_dilated.jpg を保存しました。白い部分が太ったか確認してください。")
