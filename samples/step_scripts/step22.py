# step22.py
import cv2

img  = cv2.imread("mat.jpg")                                  # もとのカラー写真
leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)           # 堆積物マスク

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

annotated = img.copy()                                        # もとを壊さないようコピーに描く
cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)     # 緑で全部の輪郭を描く

cv2.imwrite("annotated_step.jpg", annotated)
print("annotated_step.jpg を保存しました。落ち葉が緑で囲まれているか確認してください。")
