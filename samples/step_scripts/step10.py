# step10.py
import cv2
import numpy as np

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

center_h = 118        # ← step9.py で調べた値に置き換える

# マージン（許容幅）。ここを変えて結果の変化を見るのが今回の実験
H_MARGIN = 12
S_MARGIN = 70
V_MARGIN = 80

s, v = 170, 190       # マット中央の S, V（step9で調べた値）
lower = np.array([center_h - H_MARGIN, max(0, s - S_MARGIN), max(0, v - V_MARGIN)])
upper = np.array([center_h + H_MARGIN, min(255, s + S_MARGIN), min(255, v + V_MARGIN)])

mask = cv2.inRange(hsv, lower, upper)
cv2.imwrite("mat_mask2.jpg", mask)
print("下限:", lower, " 上限:", upper)
print("mat_mask2.jpg を保存しました。")
