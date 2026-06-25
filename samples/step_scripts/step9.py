# step9.py
import cv2

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# マットの中央あたり（座標は自分の写真に合わせて変える）
print("マット中央の HSV:", hsv[760, 1000])
