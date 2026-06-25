# step7.py
import cv2

for name in ["mat_bright.jpg", "mat_dark.jpg"]:
    img = cv2.imread(name)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # マットの中央あたりの画素を見る（座標は写真に合わせて調整）
    print(name, "の中央付近 HSV:", hsv[760, 1000])
