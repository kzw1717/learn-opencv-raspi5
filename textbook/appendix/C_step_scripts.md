# 付録C 全 step スクリプト集

> 第1〜8章のハンズオンで作った step スクリプト（step1〜step23）を、まとめて掲載します。
> 後から見返したいとき、コピーして動かし直したいときの早見表として使ってください。

---

## 使い方の前提

- すべて作業フォルダ `~/opencv_lesson/` の中で、VS Code の Remote-SSH 経由（Pi 上）で実行します。
- 実行は `python3 stepN.py` です。
- 画面のない Pi では結果をウィンドウ表示できないので、保存された画像は **VS Code のファイル一覧でクリックして確認**します。

### 成果物の流れ（どの画像がどこで作られるか）

step スクリプトは、前の章で作った画像を次の章で使う形でつながっています。

```
sample.jpg（第1章で撮影）
mat.jpg（第2章で撮影：マット＋落ち葉）
  → mat_mask.jpg（第3章：マット色マスク）
      → not_mat.jpg（第5章：反転）
      → leaf.jpg（第5章：範囲内のマット色でない部分＝堆積物）
  → mat_region.jpg（第6章：凸包で埋めたマット外形）
      → annotated_full.jpg（第8章：確認画像）
```

撮影は、第1章の冒頭で1回、第2章の冒頭でマット＋落ち葉の状態を1回行います。

```bash
cd ~/opencv_lesson
rpicam-jpeg -o sample.jpg --timeout 2000   # 第1章用
rpicam-jpeg -o mat.jpg --timeout 2000      # 第2章以降用（マット＋落ち葉）
```

---

## 第1章：画像は数字の表

### step1.py — 画像を読み込んで形を見る

```python
# step1.py
import cv2

# 画像をファイルから読み込む（中身は数字の表になって返ってくる）
img = cv2.imread("sample.jpg")

print(type(img))   # 何という種類のデータか
print(img.shape)   # 表の「形」＝大きさ
print(img.dtype)   # 1マスに入っている数字の種類
```

### step2.py — 1画素をのぞく

```python
# step2.py
import cv2

img = cv2.imread("sample.jpg")

# 上から100行目、左から200列目の画素を取り出す
pixel = img[100, 200]
print(pixel)
```

### step3.py — BGRの罠（色を入れ替えて壊す）

```python
# step3.py
import cv2

img = cv2.imread("sample.jpg")

# わざと青(B)と赤(R)を入れ替えてみる
swapped = img[:, :, ::-1]   # 3つ組の並びを逆さまにする

cv2.imwrite("swapped.jpg", swapped)
print("swapped.jpg を保存しました。VS Code で開いて比べてみてください。")
```

### step4.py — グレースケールで「数字の表」を実感

```python
# step4.py
import cv2

img = cv2.imread("sample.jpg")

# カラー(BGR) → 白黒(明るさだけ)に変換
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print(gray.shape)        # 形が変わる
print(gray[100, 200])    # 1マスの中身も変わる

cv2.imwrite("gray.jpg", gray)
```

---

## 第2章：色を分けて考える（HSV）

### step5.py — HSVに変換する

```python
# step5.py
import cv2

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

print("もとの画像の形:", img.shape)
print("HSVの画像の形 :", hsv.shape)

# HSVのある1点をのぞいてみる
print("ある画素のHSV:", hsv[100, 200])
```

### step6.py — H・S・Vを1枚ずつ見る

```python
# step6.py
import cv2

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 3つ組のそれぞれを取り出す
h = hsv[:, :, 0]   # 色相
s = hsv[:, :, 1]   # 彩度
v = hsv[:, :, 2]   # 明度

cv2.imwrite("hsv_h.jpg", h)
cv2.imwrite("hsv_s.jpg", s)
cv2.imwrite("hsv_v.jpg", v)
print("hsv_h.jpg / hsv_s.jpg / hsv_v.jpg を保存しました。")
```

### step7.py — 明るさを変えてHを比べる

> 事前に明るさ違いの2枚（`mat_bright.jpg`・`mat_dark.jpg`）を撮っておきます。

```python
# step7.py
import cv2

for name in ["mat_bright.jpg", "mat_dark.jpg"]:
    img = cv2.imread(name)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # マットの中央あたりの画素を見る（座標は写真に合わせて調整）
    print(name, "の中央付近 HSV:", hsv[760, 1000])
```

---

## 第3章：マスクを作る

### step8.py — inRangeでマット色を抜き出す

```python
# step8.py
import cv2
import numpy as np

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 青あたり（H=120付近）を抜き出す。値はマットの色に合わせて後で調整する
lower = np.array([100, 80, 50])
upper = np.array([140, 255, 255])

mask = cv2.inRange(hsv, lower, upper)

print("マスクの形:", mask.shape)
print("マスクに含まれる値:", np.unique(mask))   # 0と255だけのはず

cv2.imwrite("mat_mask.jpg", mask)
print("mat_mask.jpg を保存しました。")
```

### step9.py — マットの実際のHSVを調べる

```python
# step9.py
import cv2

img = cv2.imread("mat.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# マットの中央あたり（座標は自分の写真に合わせて変える）
print("マット中央の HSV:", hsv[760, 1000])
```

### step10.py — 「中心±マージン」で範囲を作る

```python
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
```

---

## 第4章：マスクの掃除（モルフォロジー）

### step11.py — オープニング（ノイズ消し）

```python
# step11.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)   # マスクは白黒で読む
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

cv2.imwrite("mask_opened.jpg", opened)
print("mask_opened.jpg を保存しました。元の mat_mask.jpg と見比べてください。")
```

### step12.py — クロージング（穴埋め）

```python
# step12.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

cv2.imwrite("mask_closed.jpg", closed)
print("mask_closed.jpg を保存しました。穴が埋まったか確認してください。")
```

### step13.py — 膨張（dilate：白を太らせる）

```python
# step13.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

dilated = cv2.dilate(mask, kernel, iterations=1)

cv2.imwrite("mask_dilated.jpg", dilated)
print("mask_dilated.jpg を保存しました。白い部分が太ったか確認してください。")
```

---

## 第5章：マスクを組み合わせる（ビット演算）

### step14.py — NOT（反転）

```python
# step14.py
import cv2

mat_mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)   # マット色＝白

not_mat = cv2.bitwise_not(mat_mask)   # 白黒を反転 ＝ マット色でない＝白

cv2.imwrite("not_mat.jpg", not_mat)
print("not_mat.jpg を保存しました。白黒が反転したか確認してください。")
```

### step15.py — AND（重なりだけ残す）

```python
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
```

---

## 第6章：形を見つける（輪郭・凸包）

### step16.py — findContoursで輪郭を取り出す

```python
# step16.py
import cv2

leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print("見つかった輪郭の数:", len(contours))
```

### step17.py — contourAreaで小さい塊を捨てる

```python
# step17.py
import cv2

leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)
contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

MIN_LEAF_AREA = 600   # これ未満は影・ノイズとみなして数えない

clumps = [c for c in contours if cv2.contourArea(c) >= MIN_LEAF_AREA]

print("全部の輪郭:", len(contours))
print("面積でふるった後の塊:", len(clumps))
```

### step18.py — convexHullで断片を1つにまとめる

```python
# step18.py
import cv2
import numpy as np

mat = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
contours, _ = cv2.findContours(mat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 十分大きい断片だけ集める（小さなゴミは無視）
MIN_MAT_FRAGMENT = 2000
pts = [c for c in contours if cv2.contourArea(c) >= MIN_MAT_FRAGMENT]

# 断片の点を全部まとめて、外側を輪ゴムで囲う＝凸包
hull = cv2.convexHull(np.vstack(pts))

print("断片の数:", len(pts))
print("凸包の頂点の数:", len(hull))
```

### step19.py — fillPolyで外形を塗りつぶしてマスクにする

```python
# step19.py
import cv2
import numpy as np

mat = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
contours, _ = cv2.findContours(mat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
pts = [c for c in contours if cv2.contourArea(c) >= 2000]
hull = cv2.convexHull(np.vstack(pts))

# 真っ黒な画像を用意し、凸包の内部を白(255)で塗る
region = np.zeros(mat.shape, dtype=np.uint8)
cv2.fillPoly(region, [hull], 255)

cv2.imwrite("mat_region.jpg", region)
print("mat_region.jpg を保存しました。マット全体が白い1枚の領域になっているか確認してください。")
```

---

## 第7章：面積を測る（被覆面積率）

### step20.py — countNonZeroで面積を数える

```python
# step20.py
import cv2

region = cv2.imread("mat_region.jpg", cv2.IMREAD_GRAYSCALE)   # 第6章で作ったマット外形
leaf   = cv2.imread("leaf.jpg",       cv2.IMREAD_GRAYSCALE)   # 第5章で作った堆積物

region_area = cv2.countNonZero(region)
leaf_area   = cv2.countNonZero(leaf)

print("計測範囲の面積:", region_area, "px")
print("堆積物の面積  :", leaf_area,   "px")
```

### step21.py — 被覆面積率を計算する

```python
# step21.py
import cv2

region = cv2.imread("mat_region.jpg", cv2.IMREAD_GRAYSCALE)
leaf   = cv2.imread("leaf.jpg",       cv2.IMREAD_GRAYSCALE)

region_area = cv2.countNonZero(region)
leaf_area   = cv2.countNonZero(leaf)

coverage_pct = 100.0 * leaf_area / region_area if region_area else 0.0
print(f"被覆面積率 = {coverage_pct:.2f}%")
```

---

## 第8章：結果を描く（可視化）

### step22.py — drawContoursで輪郭を描く

```python
# step22.py
import cv2

img  = cv2.imread("mat.jpg")                                  # もとのカラー写真
leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)           # 堆積物マスク

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

annotated = img.copy()                                        # もとを壊さないようコピーに描く
cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)     # 緑で全部の輪郭を描く

cv2.imwrite("annotated_step.jpg", annotated)
print("annotated_step.jpg を保存しました。落ち葉が緑で囲まれているか確認してください。")
```

### step23.py — putTextで数値を書き、確認画像を完成させる

```python
# step23.py
import cv2

img  = cv2.imread("mat.jpg")
leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)
region = cv2.imread("mat_region.jpg", cv2.IMREAD_GRAYSCALE)

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clumps = [c for c in contours if cv2.contourArea(c) >= 600]

region_area = cv2.countNonZero(region)
leaf_area   = cv2.countNonZero(leaf)
coverage = 100.0 * leaf_area / region_area if region_area else 0.0

annotated = img.copy()
cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)   # 堆積物：緑

label = f"coverage={coverage:.2f}%  clumps={len(clumps)}"
cv2.putText(annotated, label, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)   # 赤い文字

cv2.imwrite("annotated_full.jpg", annotated)
print("annotated_full.jpg を保存しました。左上に数値が出ているか確認してください。")
```

---

## 一覧（どの step で何を学ぶか）

| step | 章 | テーマ | 主な OpenCV |
|---|---|---|---|
| step1 | 1 | 画像の形と型 | `imread` |
| step2 | 1 | 1画素をのぞく | （配列アクセス） |
| step3 | 1 | BGRの罠 | `imwrite` |
| step4 | 1 | グレースケール | `cvtColor`(GRAY) |
| step5 | 2 | HSV変換 | `cvtColor`(HSV) |
| step6 | 2 | H/S/Vを分ける | （スライス） |
| step7 | 2 | 明るさとHの関係 | `cvtColor`(HSV) |
| step8 | 3 | マット色を抜く | `inRange` |
| step9 | 3 | 実際のHSVを調べる | （配列アクセス） |
| step10 | 3 | 中心±マージン | `inRange` |
| step11 | 4 | オープニング | `morphologyEx`(OPEN) |
| step12 | 4 | クロージング | `morphologyEx`(CLOSE) |
| step13 | 4 | 膨張 | `dilate` |
| step14 | 5 | NOT（反転） | `bitwise_not` |
| step15 | 5 | AND（重なり） | `bitwise_and` |
| step16 | 6 | 輪郭を取る | `findContours` |
| step17 | 6 | 面積でふるう | `contourArea` |
| step18 | 6 | 凸包でまとめる | `convexHull` |
| step19 | 6 | 塗りつぶす | `fillPoly` |
| step20 | 7 | 面積を数える | `countNonZero` |
| step21 | 7 | 被覆率を計算 | `countNonZero` |
| step22 | 8 | 輪郭を描く | `drawContours` |
| step23 | 8 | 数値を書く | `putText` |
