# 用語解説：NumPy

> 第1章で「画像の正体は NumPy 配列（数字の表）」だと学びました。`leaf_monitor.py` の画像・マスクはすべて NumPy 配列で、色の学習も NumPy の計算で行われています。
> NumPy は、画像処理に欠かせない「**数字の表をまとめて高速に計算する**」ライブラリです。

---

## 1. これは何？（考え方）

ふつうの Python のリストでも数字は並べられますが、何百万個もの数字（＝画像の画素）を1つずつ `for` 文で計算すると、とても遅くなります。

NumPy は、

> **たくさんの数字を「表（配列）」としてまとめ、1回の命令で一気に計算する**

ためのライブラリです。`for` で1画素ずつ回す代わりに、「配列まるごと」を足したり、条件で選んだり、数えたりできます。速いだけでなく、コードも短く読みやすくなります。

慣習で `import numpy as np` と短い別名を付けて使います（→「import文」の解説を参照）。

---

## 2. 基本の形

```python
import numpy as np

# 配列を作る
arr = np.array([10, 20, 30, 40])

# まとめて計算（for 文なしで一気に）
print(arr * 2)          # [20 40 60 80]
print(arr.sum())        # 100（合計）

# 形と型を調べる
print(arr.shape)        # (4,)  … 要素4個
print(arr.dtype)        # int64 … 数字の種類

# 条件で選ぶ（真偽配列インデックス）
print(arr[arr >= 25])   # [30 40] … 25以上だけ取り出す
```

最後の「条件で選ぶ」が、NumPy のいちばんの魅力です。`arr >= 25` は各要素を一気に判定して `[False False True True]` という真偽の配列を作り、それで `True` の場所だけ取り出します。

---

## 3. サンプルスクリプト

`leaf_monitor.py` の処理を、ミニサイズの「画像」で体験してみましょう。本物は数百万画素ですが、ここでは小さな数字の表で動きを見ます。

```python
# sample_numpy.py
import numpy as np

# 5×5 の「ミニ画像」（明るさの表）を作る
img = np.array([
    [ 10,  10, 200,  10,  10],
    [ 10, 200, 200, 200,  10],
    [200, 200, 200, 200, 200],
    [ 10, 200, 200, 200,  10],
    [ 10,  10, 200,  10,  10],
], dtype=np.uint8)

print("形:", img.shape)          # (5, 5)
print("型:", img.dtype)          # uint8

# 1点を取り出す（[行, 列]）
print("中央の値:", img[2, 2])    # 200

# スライス：真ん中の行だけ
print("3行目:", img[2, :])

# 真っ黒な同じ大きさの台紙を作る（マスク作りの定番）
mask = np.zeros(img.shape, dtype=np.uint8)

# 条件で「明るい画素」を白(255)にする＝マスク作成
mask[img >= 100] = 255
print("白い画素の数:", np.count_nonzero(mask))   # 200以上の画素数
```

実行結果（一部）：

```
形: (5, 5)
型: uint8
中央の値: 200
3行目: [200 200 200 200 200]
白い画素の数: 13
```

`mask[img >= 100] = 255` の1行で、「明るい画素だけ白くする」処理を `for` 文なしで実現しています。これはまさに、第3章の「色の範囲を白く抜き出してマスクを作る」とそっくりの発想です。最後の `np.count_nonzero` は、第7章で面積を数えた関数そのものです。

---

## 4. 代表的な使い方（画像処理での要点）

| やりたいこと | NumPy の機能 | 関係する章 |
|---|---|---|
| 数字の表を作る | `np.array([...])`、`np.zeros(形, dtype=np.uint8)` | 第6章（マスクの台紙） |
| 形・型を調べる | `.shape`、`.dtype` | 第1章 |
| 一部を取り出す（スライス） | `arr[行, 列]`、`arr[:, :, 0]` | 第1・2章 |
| 条件で選ぶ | `arr[arr >= 100]`、真偽配列 | 第3章の発想 |
| 数える | `np.count_nonzero(...)` | 第7章（面積） |
| 集計する | `np.argmax`、`np.median`、`np.bincount` | calibrate の色学習 |
| 積み重ねる | `np.vstack([...])` | 第6章（凸包の前処理） |

> **やってみよう**
> `sample_numpy.py` の `mask[img >= 100] = 255` のしきい値を `>= 100` から `>= 250` に変えてみましょう。条件に合う画素が減り、`count_nonzero` の数が小さくなるはずです。第3章で `H_MARGIN` を変えてマスクが変わったのと、同じ体験です。

---

## 5. leaf_monitor.py での実例

**(1) 真っ黒な台紙を作り、塗る** — `mat_region_from_mask()`

```python
region = np.zeros(mat_color.shape, dtype=np.uint8)   # 真っ黒な同サイズの配列
cv2.fillPoly(region, [hull], 255)                    # そこに白を塗る
```

`sample_numpy.py` の `np.zeros(...)` と同じ、「マスクの台紙作り」です。

**(2) 断片を積み重ねて凸包に渡す** — `mat_region_from_mask()`

```python
hull = cv2.convexHull(np.vstack(pts))
```

`np.vstack` で複数の断片の点を1つにまとめてから、凸包を求めています。

**(3) 真偽配列で色を学習する** — `calibrate()`

```python
valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)   # 条件に合う画素＝True
peak = int(np.argmax(np.bincount(Hc[valid].ravel(), minlength=180)))  # 最も多い色相
s_med = int(np.median(Sc[matpix]))                          # 彩度の代表値
```

ここが NumPy の真骨頂です。「彩度・明度が条件に合う画素」を真偽配列 `valid` で一気に選び、その画素の色相を集計して、いちばん多い色相＝マット色を求めています。もし `for` 文で数百万画素を1つずつ調べたら、とても遅くなります。NumPy だからこそ、Pi のような小さなコンピュータでも実用的な速さで動くのです。

---

## 6. まとめ

- NumPy は「数字の表（配列）をまとめて高速に計算する」ライブラリ。画像処理の土台。
- `np.array`・`np.zeros` で配列を作り、`.shape`・`.dtype` で形と型を調べる。
- スライス（`arr[行, 列]`、`arr[:, :, 0]`）で一部を取り出す。
- 真偽配列（`arr[arr >= 100]`）で、条件に合う画素を `for` 文なしで一気に選べる。
- `np.count_nonzero`（数える）・`np.argmax`・`np.median`・`np.bincount`（集計）・`np.vstack`（積む）などが `leaf_monitor.py` で活躍。
- 画像＝NumPy 配列なので、OpenCV と NumPy はいつもセットで使われる。
