# step3.py
import cv2

img = cv2.imread("sample.jpg")

# わざと青(B)と赤(R)を入れ替えてみる
swapped = img[:, :, ::-1]   # 3つ組の並びを逆さまにする

cv2.imwrite("swapped.jpg", swapped)
print("swapped.jpg を保存しました。VS Code で開いて比べてみてください。")
