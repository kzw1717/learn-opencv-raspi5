# step17.py
import cv2

leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)
contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

MIN_LEAF_AREA = 600   # これ未満は影・ノイズとみなして数えない

clumps = [c for c in contours if cv2.contourArea(c) >= MIN_LEAF_AREA]

print("全部の輪郭:", len(contours))
print("面積でふるった後の塊:", len(clumps))
