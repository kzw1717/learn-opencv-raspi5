# step4.py
import cv2

img = cv2.imread("sample.jpg")

# カラー(BGR) → 白黒(明るさだけ)に変換
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print(gray.shape)        # 形が変わる
print(gray[100, 200])    # 1マスの中身も変わる

cv2.imwrite("gray.jpg", gray)
