# step1.py
import cv2

# 画像をファイルから読み込む（中身は数字の表になって返ってくる）
img = cv2.imread("sample.jpg")

print(type(img))   # 何という種類のデータか
print(img.shape)   # 表の「形」＝大きさ
print(img.dtype)   # 1マスに入っている数字の種類
