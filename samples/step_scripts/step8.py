# step8.py
import cv2
import numpy as np

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 青あたり（H=120付近）を抜き出す。値はマットの色に合わせて後で調整する
lower = np.array([100, 80, 50])
upper = np.array([140, 255, 255])

mask = cv2.inRange(hsv, lower, upper)

print("マスクの形:", mask.shape)
print("マスクに含まれる値:", np.unique(mask))   # 0と255だけのはず

cv2.imwrite("mat_mask.jpg", mask)
print("mat_mask.jpg を保存しました。")
