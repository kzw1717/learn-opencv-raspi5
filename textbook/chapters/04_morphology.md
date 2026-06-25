# 第4章 マスクの掃除（モルフォロジー）

> 第3章で作ったマスクをよく見ると、たいてい「汚れて」います。
> 小さな白い点がぱらぱら散っていたり、白い領域の中に黒い穴があいていたり。
> この章では、マスクをきれいに整える画像処理 **モルフォロジー** を学びます。地味ですが、計測の安定にとても効きます。

---

## 4.1 この章のゴール

この章を終えると、次のことができるようになります。

- マスクに混じる「小さなノイズ」「小さな穴」がなぜ問題になるかを説明できる
- `cv2.getStructuringElement` で、処理に使う「ブラシ」の形を作れる
- **オープニング**（小さな白い点を消す）と**クロージング**（小さな黒い穴を埋める）を使い分けられる
- **膨張（dilate）** で白い領域を少し太らせられる
- `leaf_monitor.py` がマスクをどう整えているか理解できる

---

## 4.2 なぜマスクを掃除するのか

第3章で作った `mat_mask.jpg` をよく見ると、たとえばこんな汚れがあります。

- マットの外の関係ない場所に、**小さな白い点**がぽつぽつ（似た色のゴミや、光の反射を拾ってしまった）
- マットの白い領域の中に、**小さな黒い穴**（落ち葉の影や模様で、一部がマット色から外れた）

このまま「白い部分の数」や「白い領域の面積」を数えると、ノイズのぶんだけ結果がブレてしまいます。`leaf_monitor.py` は1日に何度も自動で計測するので、こうした小さなブレが積み重なると、トレンドが読みにくくなります。

そこで、**計測の前にマスクを掃除して形を整える**のです。この掃除の技術が「モルフォロジー処理」です。

---

## 4.3 「ブラシ」を用意する：getStructuringElement

モルフォロジー処理は、ある形の「ブラシ（カーネル）」でマスクをなぞるように働きます。まずそのブラシを作ります。

```python
import cv2
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
```

- `cv2.MORPH_ELLIPSE` … ブラシの形を「楕円（だ円）」にする。角がなく自然な仕上がりになるので、`leaf_monitor.py` でも使われています。
- `(5, 5)` … ブラシの大きさ（5×5ピクセル）。**大きいほど効き目が強く**、小さな汚れだけでなく大きめのものまで影響します。

このブラシの大きさが、`leaf_monitor.py` の `MORPH_KERNEL = 5` という設定にあたります。

---

## 4.4 オープニング：小さな白い点を消す

**オープニング**は、「小さな白い出っぱりやノイズを消す」処理です。ブラシより小さい白い点は消え、本体の大きな白い領域はほぼそのまま残ります。

第3章で作った `mat_mask.jpg` を掃除してみましょう。

```python
# step11.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)   # マスクは白黒で読む
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

cv2.imwrite("mask_opened.jpg", opened)
print("mask_opened.jpg を保存しました。元の mat_mask.jpg と見比べてください。")
```

`mat_mask.jpg` と `mask_opened.jpg` を VS Code で並べて開いてください。背景に散っていた**小さな白い点が消えて**、すっきりしているはずです。

> ポイント：`cv2.imread(..., cv2.IMREAD_GRAYSCALE)` でマスクを白黒のまま読み込んでいます。マスクはもともと白黒なので、3つ組のカラーで読む必要はありません。`leaf_monitor.py` も、保存したマスク（region.png など）をこの白黒モードで読み込んでいます。

> **やってみよう 1**
> `kernel` の大きさを `(5, 5)` から `(15, 15)` に変えて実行してみましょう。ブラシが大きくなると、消える白い部分も大きくなります。やりすぎると本来のマットまで削れてしまうことを確認してください。

---

## 4.5 クロージング：小さな黒い穴を埋める

**クロージング**は、オープニングの逆向きで、「小さな黒い穴やすき間を埋める」処理です。白い領域の中の小さな黒い点が白く埋まります。

```python
# step12.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

cv2.imwrite("mask_closed.jpg", closed)
print("mask_closed.jpg を保存しました。穴が埋まったか確認してください。")
```

`MORPH_CLOSE` を指定し、`iterations=2`（2回くりかえし）で少し強めに効かせています。白い領域の中にあった小さな黒い穴が**埋まって**、なめらかになっているはずです。

オープニングとクロージングは、しばしば**セット**で使われます。「まずオープニングでノイズを消し、次にクロージングで穴を埋める」と、白い領域がきれいなひと固まりになります。`leaf_monitor.py` でも、落ち葉のマスクに対してこの順で両方かけています。

> **やってみよう 2**
> 「オープニングだけ」「クロージングだけ」「オープニング→クロージングの順」の3つを作って見比べてみましょう。3つ目が一番きれいになるはずです。なぜ順番が大事なのか考えてみてください。

---

## 4.6 膨張（dilate）：白い領域を少し太らせる

**膨張（dilate）** は、白い領域を全体的にひとまわり太らせる処理です。

これは何に使うのでしょうか。`leaf_monitor.py` では、「鉢」を計測から除外するためのマスクを作るとき、鉢のマスクを少し太らせています。なぜなら、抜き出した鉢の輪郭はぴったりすぎて、**鉢の縁がわずかに取りこぼされて堆積物と誤検出される**ことがあるからです。少し太らせて余裕を持たせることで、縁の取りこぼしを防ぎます。

```python
# step13.py
import cv2

mask = cv2.imread("mat_mask.jpg", cv2.IMREAD_GRAYSCALE)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

dilated = cv2.dilate(mask, kernel, iterations=1)

cv2.imwrite("mask_dilated.jpg", dilated)
print("mask_dilated.jpg を保存しました。白い部分が太ったか確認してください。")
```

`mat_mask.jpg` と `mask_dilated.jpg` を比べると、白い領域がひとまわり**膨らんで**いるはずです。ここで使った `(9, 9)` というブラシの大きさが、`leaf_monitor.py` の `POT_DILATE = 9`（鉢マスクをどれだけ太らせるか）にあたります。

> **やってみよう 3**
> 仕様書のトラブルシューティングに「鉢の縁が堆積物として残るときは `POT_DILATE` を大きくする」とあります。`(9, 9)` を `(21, 21)` にすると白い部分はもっと太ります。ただし太らせすぎると、鉢の近くにある本物の堆積物まで「鉢」として消してしまいます。このトレードオフを確認してください。

---

## 4.7 `leaf_monitor.py` への橋渡し

この章で学んだ処理は、`leaf_monitor.py` のあちこちに出てきます。

**(1) ブラシを作る** — `analyze()`・`calibrate()` の両方

```python
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL, MORPH_KERNEL))
```

私たちの `kernel` と同じ、楕円のブラシです。`MORPH_KERNEL` が大きさ（既定値5）です。

**(2) ノイズ消し＋穴埋め** — `analyze()` の落ち葉マスク処理

```python
leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN,  k, iterations=1)
leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, k, iterations=2)
```

まさに「オープニングでノイズを消し、クロージングで穴を埋める」をこの順で行っています。`step11.py`〜`step12.py` でやったことそのものです。

**(3) 鉢マスクを太らせる** — `calibrate()` の中

```python
dk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (POT_DILATE, POT_DILATE))
pot = cv2.dilate(pot, dk, iterations=1)
```

`step13.py` と同じく、鉢マスクを少し太らせて縁の取りこぼしを防いでいます。`POT_DILATE = 9` がブラシの大きさです。

このように、第3章で作った「ざらついたマスク」を、この章のモルフォロジーで「なめらかなマスク」に整えてから、次のステップに渡しています。計測の安定は、こうした地道な掃除に支えられているのです。

---

## 4.8 この章のまとめ

- マスクには小さな白い点（ノイズ）や黒い穴が混じりがちで、そのまま数えると結果がブレる。
- `cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))` で処理用のブラシ（カーネル）を作る。大きいほど効き目が強い。
- **オープニング（`MORPH_OPEN`）** … 小さな白い点を消す。
- **クロージング（`MORPH_CLOSE`）** … 小さな黒い穴を埋める。オープニングとセットで使うときれい。
- **膨張（`cv2.dilate`）** … 白い領域を太らせる。鉢の縁の取りこぼし防止に使う（`POT_DILATE`）。

---

## 4.9 確認問題

1. マスクの背景に散らばった小さな白い点（ノイズ）を消したい。オープニングとクロージングのどちらを使うべきか答えなさい。
2. 白い領域の中にあいた小さな黒い穴を埋めたい。どちらを使うべきか答えなさい。
3. `cv2.getStructuringElement` で作るブラシ（カーネル）を大きくすると、モルフォロジー処理の効き目はどうなるか説明しなさい。
4. `leaf_monitor.py` が鉢マスクに膨張（dilate）をかけているのはなぜか、説明しなさい。また、太らせすぎると何が問題になるか答えなさい。

---

**次章予告 ── 第5章「マスクを組み合わせる（ビット演算）」**
きれいなマスクが用意できました。次はいよいよ「計測範囲の中で・マット色でないもの＝堆積物」という肝心の取り出しを行います。これは複数のマスクを論理（かつ・でない）で組み合わせることで実現します。次章では `cv2.bitwise_and`（かつ）と `cv2.bitwise_not`（でない）を学び、`leaf_monitor.py` が落ち葉を取り出す核心の1行を読み解きます。
