# step6.py
import cv2

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 3つ組のそれぞれを取り出す
h = hsv[:, :, 0]   # 色相
s = hsv[:, :, 1]   # 彩度
v = hsv[:, :, 2]   # 明度

cv2.imwrite("hsv_h.jpg", h)
cv2.imwrite("hsv_s.jpg", s)
cv2.imwrite("hsv_v.jpg", v)
print("hsv_h.jpg / hsv_s.jpg / hsv_v.jpg を保存しました。")
