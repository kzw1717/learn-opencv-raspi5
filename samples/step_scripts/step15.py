# step15.py
import cv2
import numpy as np

mat_mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
h, w = mat_mask.shape

# 仮の計測範囲：中央の大きな長方形を白く塗ったマスク（本番は第6章で作る）
region = np.zeros((h, w), dtype=np.uint8)
cv2.rectangle(region, (w//5, h//5), (w*4//5, h*4//5), 255, -1)  # -1で内部を塗りつぶし

# 「マット色でない」
not_mat = cv2.bitwise_not(mat_mask)

# 「範囲の中」かつ「マット色でない」＝堆積物
leaf = cv2.bitwise_and(region, not_mat)

cv2.imwrite("region.jpg", region)
cv2.imwrite("leaf.jpg", leaf)
print("region.jpg（仮の範囲）と leaf.jpg（取り出した堆積物）を保存しました。")
