# 付録E OpenCV のための NumPy 入門

> このテキストでは「画像＝NumPy 配列（数字の表）」と何度も出てきました。
> この付録は、その NumPy を**実機のカメラで撮った画像を使って**手を動かしながら学び、最終的に `leaf_monitor.py` の中の NumPy のおおまかな意味が読めるようになることを目指します。
> あわせて、前提となる「配列」と「オブジェクト／ファイルオブジェクト」も、関連する場面で順に押さえていきます。

---

## E.1 この付録のゴール

`leaf_monitor.py` には、OpenCV だけでなく **NumPy** がたくさん使われています。特にマットの色を学習する `calibrate()` には、

```python
valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)
peak = int(np.argmax(np.bincount(Hc[valid].ravel(), minlength=180)))
```

のような、初めて見ると暗号のような行があります。この付録を終えるころには、こうした行の **「だいたい何をしているか」** が説明できるようになります。

進め方は、**最初にカメラで1枚撮り、その同じ画像を各節で少しずつ違う角度から処理する**スタイルです。撮影には Raspberry Pi の CLI コマンドを使います。

## 準備：カメラで1枚撮り、配列として読み込む

まず作業フォルダで、マットの上に落ち葉をいくつか置いた状態を1枚撮ります。以降の節は、すべてこの `np_sample.jpg` を使います。

```bash
cd ~/opencv_lesson
rpicam-jpeg -o np_sample.jpg --timeout 2000
```

撮影は Python から CLI コマンドを呼び出す形でもできます。次の `e1.py` は「撮る → 配列として読み込む → その正体を表示する」を1本にまとめたものです。

```python
# e1.py — CLIで撮影し、画像がNumPy配列であることを確かめる
import subprocess
import cv2

# 【工夫】PythonからCLIコマンド rpicam-jpeg を実行して1枚撮る
subprocess.run(["rpicam-jpeg", "-o", "np_sample.jpg", "--timeout", "2000"], check=True)

img = cv2.imread("np_sample.jpg")     # 読み込むと NumPy配列(ndarray)が返る

print("種類 :", type(img))            # <class 'numpy.ndarray'>
print("次元 :", img.ndim)             # 3（縦・横・色）
print("形   :", img.shape)            # (縦, 横, 3)
print("型   :", img.dtype)            # uint8（0〜255）
```

```bash
python3 e1.py
```

`<class 'numpy.ndarray'>` と表示されれば、第1章で学んだ「画像の正体は NumPy 配列」が確認できたことになります。ここから、その配列をいろいろに料理していきます。

---

## E.2 まず「配列」とは

NumPy に入る前に、土台の「配列」をはっきりさせます。**配列**とは「**同じような値を順番に並べた入れもの**」で、**番号（インデックス）で1つずつ取り出せる**のが特徴です。番号は **0 から始まります**（1番目が `[0]`）。

Python で「並んだデータ」を表すものには、おもに次があります。

- **list（リスト）`[ ]`** … 1次元（1列に並ぶ）。あとから中身を変えられる。
- **tuple（タプル）`( )`** … 1次元。変えられない。
- **numpy.ndarray** … 多次元（表・立体）。画像・マスクの正体。

ちがいを小さなコードで体感しましょう。これは画像を使わない、純粋な配列の確認です。

```python
# e2_concept.py — list/tuple と NumPy配列の「次元」を見比べる
import numpy as np

lst = [10, 20, 30]              # リスト（1次元）
tpl = (2028, 1520)             # タプル（1次元・変更不可）
print("リストの2番目:", lst[1])  # 20（0始まりなので2番目は[1]）

a1 = np.array([10, 20, 30])     # 1次元のNumPy配列
a2 = np.array([[1, 2, 3],
               [4, 5, 6]])      # 2次元のNumPy配列（表）

print("a1.shape =", a1.shape)   # (3,)      … 1次元
print("a2.shape =", a2.shape)   # (2, 3)    … 2行3列の表
print("a2[1, 2] =", a2[1, 2])   # 6（2行目・3列目）
```

`list` や `tuple` は「1列に並んだもの」、NumPy の配列は「**縦横に広がった数字の表**」にもなれる、という違いが要点です。画像は色の数字が縦横にびっしり並んだ表なので、自然と多次元の NumPy 配列になります。

> **やってみよう**
> `a2[0, :]`（1行目を丸ごと）、`a2[:, 1]`（2列目を丸ごと）を表示してみましょう。`:`（コロン）が「その方向は全部」という意味だと分かります。これがスライスで、画像のチャンネル抜き出しに使います（E.4）。

---

## E.3 NumPy 配列は「オブジェクト」でもある

ここで「オブジェクト」という考え方を挟みます。NumPy 配列は「配列」であると同時に、**データ（属性）と動作（メソッド）を持つオブジェクト**でもあります。

- **属性** … オブジェクトが持つデータ。`.` で取り出す（例：`img.shape`）。
- **メソッド** … オブジェクトにできる動作。`.` で呼ぶ（例：`img.copy()`）。

撮った画像で確かめます。

```python
# eo1.py — 配列＝オブジェクト（属性とメソッドを持つ）
import cv2

img = cv2.imread("np_sample.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 属性（持っているデータ）
print("形(shape) :", img.shape)
print("型(dtype) :", img.dtype)
print("次元(ndim):", img.ndim)

# メソッド（できる動作）
print("最大の明るさ max :", gray.max())
print("平均の明るさ mean:", gray.mean())
copy = img.copy()                      # 複製を作るメソッド
print("コピーの形:", copy.shape)
```

`.shape`（属性）と `.max()`（メソッド、最後に `()` が付く）の見た目の違いに注目してください。

### 自作のオブジェクトで「属性・メソッド」を体感する

`leaf_monitor.py` は自分でクラスを定義しませんが、`Picamera2()` などライブラリのオブジェクトを使います。その理解の足場として、小さなクラスを自分で作ってみましょう。撮った画像の明るさを扱う「鉢画像オブジェクト」です。

```python
# eo2.py — 自作クラスで属性・メソッドを理解する
import cv2

class PotImage:                       # オブジェクトの設計図（クラス）
    def __init__(self, path):
        self.path = path              # 属性：画像のパス
        self.img = cv2.imread(path)   # 属性：画像（NumPy配列）

    def brightness(self):             # メソッド：平均の明るさを返す
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        return float(gray.mean())

    def report(self):                 # メソッド：状態を表示する
        print(f"{self.path}: 平均の明るさ = {self.brightness():.1f}")

pot = PotImage("np_sample.jpg")       # インスタンス化（実体を作る）
print("パス属性:", pot.path)          # 属性アクセス
pot.report()                          # メソッド呼び出し
```

`pot = PotImage(...)` で実体を作り、`pot.report()` で動作を命じる——この構図は、`leaf_monitor.py` の `picam2 = Picamera2()` → `picam2.start()` とまったく同じです。「もの（オブジェクト）に動作（メソッド）を命じる」のがオブジェクトの使い方だと覚えてください。

---

## E.4 画像＝NumPy 配列（画素アクセスとスライス）

配列だと分かったので、中身を取り出します。画像は **`[行, 列]`** で1画素を取り出せ、画素はカラーでは **BGR の3つ組**です。

```python
# e2.py — 画素を番号で取り出す
import cv2

img = cv2.imread("np_sample.jpg")

px = img[100, 200]                # 上から100・左から200の画素（BGRの3つ組）
print("画素[100,200] =", px)
print("青(B) =", px[0], " 緑(G) =", px[1], " 赤(R) =", px[2])  # BGR順
```

**スライス**を使うと、色チャンネルをまとめて取り出せます。第2章でやった H・S・V 分離は、これです。

```python
# e3.py — スライスでH/S/Vを分ける
import cv2

img = cv2.imread("np_sample.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

h = hsv[:, :, 0]   # 全行・全列の「0番目（色相H）」だけ
s = hsv[:, :, 1]
v = hsv[:, :, 2]

cv2.imwrite("np_h.jpg", h)
cv2.imwrite("np_s.jpg", s)
cv2.imwrite("np_v.jpg", v)
print("np_h.jpg / np_s.jpg / np_v.jpg を保存しました。VS Codeで開いて見比べてください。")
```

> **やってみよう**
> `img[:, :, ::-1]` を保存して、もとの `np_sample.jpg` と見比べてみましょう。`::-1` は「並びを逆さに」する書き方で、BGR↔RGB が入れ替わって色が壊れます（第1章の BGR の罠）。

`leaf_monitor.py` でも、`Hc, Sc, Vc = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]` と、まったく同じスライスでチャンネルを分けています。

---

## E.5 配列をまとめて計算する（for を使わない）

NumPy の最大の強みは、**配列まるごとを1回の命令で計算できる**ことです。何百万個もの画素を `for` で1つずつ回さず、一気に処理します。

```python
# e5_calc.py — 配列はまとめて計算できる
import numpy as np

a = np.array([10, 100, 200, 50])

print("全部2倍 :", a * 2)          # [ 20 200 400 100]
print("全部+5  :", a + 5)          # [ 15 105 205  55]
print("100以上か:", a >= 100)       # [False  True  True False]  ← 真偽の配列が返る
```

注目は最後の `a >= 100` です。**比較すると、各要素が条件に合うかを表す True/False の配列が一気にできます**。これが次の節「真偽配列」の土台で、`leaf_monitor.py` の色判定の心臓部です。同じことが画像（2次元・3次元の配列）でもそのまま成り立ちます。

> **やってみよう**
> `gray = cv2.cvtColor(cv2.imread("np_sample.jpg"), cv2.COLOR_BGR2GRAY)` を読み込み、`gray >= 128` を `print` してみましょう。画像全体について「明るいか？」が True/False の表で一気に求まります。

---

## E.6 真偽配列で「条件に合う画素だけ」選ぶ

E.5 の真偽配列を使うと、「条件に合う画素だけ」を選んだり、白く塗ったりできます。第3〜4章で作ったマスクと同じことを、NumPy だけでやってみます。

```python
# e4.py — 真っ黒な台紙に、明るい画素だけ白を塗る／白を数える
import cv2
import numpy as np

img  = cv2.imread("np_sample.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

mask = np.zeros(gray.shape, dtype=np.uint8)   # 真っ黒な同サイズ配列（台紙）
mask[gray >= 128] = 255                       # 明るい画素だけ白に（まとめて代入）

white = np.count_nonzero(mask)                # 白い（0でない）画素を数える＝面積
print("白い画素の数 =", white)
cv2.imwrite("np_mask.jpg", mask)
print("np_mask.jpg を保存しました。")
```

`mask[gray >= 128] = 255` の1行で、「明るい画素の場所だけ白くする」が `for` 文なしで実現しています。`np.count_nonzero` は、第7章で面積を数えた考え方そのものです（`leaf_monitor.py` では同じ働きの `cv2.countNonZero` も使われます）。

### 結果をファイルに残す（ファイルオブジェクト）

数えた結果は、ファイルに記録しておくと後で見返せます。ここで「**ファイルオブジェクト**」を使います。`open(...)` を実行すると、開いたファイルを表すオブジェクト（取っ手）が返り、それを通して書き込みます。

```python
# eo3.py — ファイルオブジェクトでCSVに結果を追記する
import cv2
import numpy as np
import csv
import os
from datetime import datetime

img  = cv2.imread("np_sample.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

brightness = float(gray.mean())
white = int(np.count_nonzero(gray >= 128))
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

new_file = not os.path.exists("np_log.csv")
# 【ファイルオブジェクト】open が返す f を通して書く。with なので自動で閉じる。
with open("np_log.csv", "a", newline="") as f:   # "a" は追記モード
    w = csv.writer(f)                             # f（ファイルオブジェクト）をcsvに渡す
    if new_file:
        w.writerow(["timestamp", "brightness", "white_px"])
    w.writerow([ts, f"{brightness:.1f}", white])

print("np_log.csv に1行追記しました。VS Codeで開いて確認してください。")
```

`with open(...) as f:` の `f` がファイルオブジェクトです。`"a"`（追記）で開き、`csv.writer(f)` に渡して1行書き、ブロックを抜けると自動で閉じます。これは `leaf_monitor.py` の `append_log()` の

```python
with open(LOG_CSV, "a", newline="") as f:
    w = csv.writer(f)
    ...
    w.writerow([timestamp, f"{coverage:.3f}", clumps])
```

と、そっくり同じ形です。`eo3.py` を何度か実行すると、`np_log.csv` に行が積み上がっていきます（→ ログがたまる感覚）。

---

## E.7 集計の道具（色学習の心臓部）

いよいよ E.1 で見せた「暗号のような行」に挑みます。`leaf_monitor.py` の `calibrate()` は、撮った画像から **いちばん多い色相＝マット色** を見つけます。撮った画像でそのまま再現してみましょう。

```python
# e5.py — 有彩色の画素を選び、最も多い色相＝マット色を求める
import cv2
import numpy as np

img = cv2.imread("np_sample.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

SAT_MIN, VAL_MIN, VAL_MAX = 50, 40, 245

# ① 真偽配列：彩度が十分・明るすぎず暗すぎない画素を True に（E.5/E.6の応用）
valid = (S > SAT_MIN) & (V > VAL_MIN) & (V < VAL_MAX)
print("有彩色の画素数 =", np.count_nonzero(valid))

# ② Trueの画素の色相だけ集めて、色相ごとの個数を数える（ヒストグラム）
hist = np.bincount(H[valid].ravel(), minlength=180)

# ③ いちばん個数が多い色相の位置＝マットの色相
peak = int(np.argmax(hist))
print("最も多い色相 peak =", peak)

# ④ その色相の近くの画素から、代表の彩度・明度（中央値）を取る
H_MARGIN = 12
hue_dist = np.minimum(np.abs(H.astype(int) - peak), 180 - np.abs(H.astype(int) - peak))
matpix = valid & (hue_dist <= H_MARGIN)
print("代表 S,V =", int(np.median(S[matpix])), int(np.median(V[matpix])))
```

1行ずつの「おおまかな意味」はこうです。

- `valid = (...) & (...) & (...)` … **真偽配列**。各画素が「色付きとみなせるか」を一括判定（E.5）。
- `H[valid]` … 真偽配列で **True の画素の色相だけ取り出す**（条件で選ぶ、E.6）。
- `np.bincount(..., minlength=180)` … 色相 0〜179 ごとに **何個あるか数える**（ヒストグラム）。
- `np.argmax(...)` … いちばん多かった位置＝**最頻の色相**を返す。これがマット色。
- `np.median(...)` … 代表値として**中央値**を取る。
- `np.abs` / `np.minimum` … 色相の「距離」を求める計算（H は円状なので両回りの近いほうを取る）。

細かい数式は分からなくても大丈夫です。**「色付きの画素を選び、いちばん多い色相をマット色と決めている」**という流れがつかめれば、この付録のゴールは達成です。

---

## E.8 配列を作る・積む・型を変える

`leaf_monitor.py` に出てくる残りの NumPy も、小さく確認しておきます。

```python
# e6.py — 配列の作成・結合・型変換
import numpy as np

# リスト → 配列（load_mat_config と同じ）
lower = np.array([108, 100, 110])
print("配列にした下限 =", lower, " 型 =", lower.dtype)

# 真っ黒な台紙を作る（マスク作りの定番、E.6でも使用）
canvas = np.zeros((3, 4), dtype=np.uint8)
print("zerosで作った台紙:\n", canvas)

# 縦に積み重ねて1つにまとめる（mat_region_from_mask の凸包の前処理と同じ発想）
a = np.array([[1, 2]])
b = np.array([[3, 4]])
print("vstackで結合:\n", np.vstack([a, b]))

# 型を変える（uint8へ）
print("astypeで型変換 =", lower.astype(np.uint8).dtype)
```

これで、`leaf_monitor.py` が使う NumPy の道具（`array`・`zeros`・`vstack`・`astype`・`uint8`）が一通りそろいました。

---

## E.9 仕上げ：leaf_monitor.py の NumPy を読む

ここまでの体験で、`leaf_monitor.py` の NumPy 部分が読めるようになっているはずです。実コードから抜き出して回収します。

| leaf_monitor.py の行 | おおまかな意味 | この付録の節 |
|---|---|---|
| `np.array(cfg["lower"])` | リスト→配列 | E.8 |
| `hsv[:, :, 0]`（`Hc, Sc, Vc = ...`） | スライスでチャンネル分離 | E.4 |
| `img_bgr.copy()` | 配列（オブジェクト）の複製メソッド | E.3 |
| `valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)` | 真偽配列で一括判定 | E.5・E.6 |
| `np.count_nonzero(valid)` | True（0でない）の数を数える | E.6 |
| `Hc[valid].ravel()` | 条件で選び、1次元に平らに | E.6・E.3 |
| `np.bincount(..., minlength=180)` | 色相ごとの個数を数える | E.7 |
| `np.argmax(...)` | 最頻の色相の位置を返す | E.7 |
| `np.median(...)` | 代表値（中央値）を取る | E.7 |
| `np.minimum(np.abs(...), ...)` | 色相の距離を計算 | E.7 |
| `np.zeros(mat_color.shape, dtype=np.uint8)` | 真っ黒な台紙を作る | E.6・E.8 |
| `np.vstack(pts)` | 断片の点を結合 | E.8 |
| `upper.astype(np.uint8)` | 型を変える | E.8 |

そして、オブジェクトとファイルオブジェクトの回収です。

- `picam2 = Picamera2()` → `picam2.start()` … オブジェクトのインスタンス化とメソッド呼び出し（E.3 の `PotImage` と同じ構図）。
- `with open(LOG_CSV, "a") as f: w = csv.writer(f)` … ファイルオブジェクトでログを追記（E.6 の `eo3.py` と同じ形）。

> ひとつ注意：面積を数える関数は、`calibrate()` では NumPy の `np.count_nonzero`、`analyze()` では OpenCV の `cv2.countNonZero` が使われています。**名前も働きもそっくり**ですが、前者は NumPy、後者は OpenCV の道具、という違いだけ頭の隅に置いておきましょう。

---

## E.10 まとめと確認問題

### まとめ

- 画像は NumPy 配列。番号（0始まり）で画素を取り出し、スライス（`:`）でチャンネルを分けられる。
- NumPy 配列はオブジェクトでもあり、`.shape`（属性）や `.copy()`（メソッド）を持つ。
- 比較すると**真偽配列**ができ、それで「条件に合う画素だけ」を選んだり白く塗ったりできる（`for` 不要）。
- `count_nonzero`（数える）・`bincount`・`argmax`・`median`（集計）で、マット色の学習ができる。
- `array`・`zeros`・`vstack`・`astype` で、配列を作る・積む・型を変える。
- 結果はファイルオブジェクト（`with open(...) as f`）で CSV に残せる。

### 確認問題

1. NumPy 配列 `a = np.array([5, 30, 80])` に対して `a >= 30` を計算すると、何が返るか答えなさい。
2. 画像 `img` から「上から50・左から60の画素の赤(R)の明るさ」を取り出す書き方を、BGR の順番に注意して書きなさい。
3. `mask[gray >= 128] = 255` は何をしているか、日本語で説明しなさい。
4. `leaf_monitor.py` の `peak = int(np.argmax(np.bincount(Hc[valid].ravel(), minlength=180)))` が、おおまかに何を求めているか説明しなさい。
5. `picam2 = Picamera2()` と `pot = PotImage("np_sample.jpg")` に共通する「オブジェクトの作り方」の名前を答えなさい。

（解答例は付録D の方針に合わせ、要点が合っていれば自分の言葉で書けていれば正解です。）
