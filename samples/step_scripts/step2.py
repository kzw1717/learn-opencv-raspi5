# step2.py
import cv2

img = cv2.imread("sample.jpg")

# 上から100行目、左から200列目の画素を取り出す
pixel = img[100, 200]
print(pixel)
