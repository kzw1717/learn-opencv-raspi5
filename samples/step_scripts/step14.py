# step14.py
import cv2

mat_mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)   # マット色＝白

not_mat = cv2.bitwise_not(mat_mask)   # 白黒を反転 ＝ マット色でない＝白

cv2.imwrite("not_mat.jpg", not_mat)
print("not_mat.jpg を保存しました。白黒が反転したか確認してください。")
