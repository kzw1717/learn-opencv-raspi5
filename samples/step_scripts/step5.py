# step5.py
import cv2

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

print("もとの画像の形:", img.shape)
print("HSVの画像の形 :", hsv.shape)

# HSVのある1点をのぞいてみる
print("ある画素のHSV:", hsv[100, 200])
