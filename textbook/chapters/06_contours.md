# 第6章 形を見つける（輪郭・凸包）

> 堆積物やマットの「場所」はマスクで分かりました。
> でも「塊がいくつあるか」「マット全体の外形はどこか」を知るには、白い領域の**ふちどり（輪郭）**を見つける必要があります。
> この章では輪郭まわりの道具を学び、`leaf_monitor.py` が鉢で分断されたマットを1つに復元する、賢い仕組みを解き明かします。

---

## 6.1 この章のゴール

この章を終えると、次のことができるようになります。

- **輪郭（contour）** とは「白い領域のふちどり」だと説明できる
- `cv2.findContours` で輪郭を取り出し、`cv2.contourArea` で面積を測れる
- 面積で小さな輪郭（ノイズ）をふるい落とす方法が分かる
- `cv2.convexHull`（凸包）で、バラバラの断片を1つの外形にまとめられる
- `cv2.fillPoly` で、その外形を塗りつぶしてマスクにできる

---

## 6.2 輪郭（contour）ってなに？

**輪郭**は、白い領域の「ふちどり（境界線）」のことです。塗り絵で言えば、色を塗る前の「黒い線」にあたります。

輪郭が手に入ると、次のようなことができます。

- 白い塊が**いくつ**あるか数える（輪郭の本数＝塊の数）
- それぞれの塊の**面積**を測る
- 塊を線で**囲んで**確認画像を作る（第8章）

`leaf_monitor.py` は、これを使って「堆積物の塊が何個あるか（clumps）」を数えたり、「マットの外形」を求めたりしています。

---

## 6.3 findContours で輪郭を取り出す

第5章で作った堆積物マスク `leaf.jpg` から、輪郭を取り出してみましょう。

```python
# step16.py
import cv2

leaf = cv2.imread("leaf.jpg", cv2.IMREAD_GRAYSCALE)

contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print("見つかった輪郭の数:", len(contours))
```

```bash
python3 step16.py
```

`cv2.findContours` の3つの引数・戻り値を説明します。

- 第1引数：輪郭を探したい白黒マスク。
- `cv2.RETR_EXTERNAL`：**いちばん外側の輪郭だけ**を取る、という指定。塊の中に穴があっても、外側の囲いだけを取ります。塊を数えるのにちょうどよい設定です。
- `cv2.CHAIN_APPROX_SIMPLE`：輪郭を表す点を**間引いて軽く**する指定。たとえばまっすぐな辺は両端の2点だけで表します。データが小さくなり速くなります。
- 戻り値：`contours`（輪郭のリスト）と、もう1つ（輪郭の親子関係。今回は使わないので `_` で受け捨て）。

`len(contours)` が、見つかった白い塊のおおよその数です。ただし、この中には影やノイズによる**ごく小さな塊**も混じっています。次でふるい落とします。

> `cv2.imread(..., cv2.IMREAD_GRAYSCALE)` でマスクを白黒のまま読み込んでいる点に注目してください。輪郭処理は白黒マスクに対して行います。

---

## 6.4 contourArea で面積を測り、小さいものを捨てる

`cv2.contourArea` は、1つの輪郭が囲む**面積（ピクセル数）**を返します。これを使って、「小さすぎる塊はノイズとして数えない」というふるい分けをします。

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

`MIN_LEAF_AREA` 以上の面積を持つ輪郭だけを `clumps` に残しています。実行すると、ふるった後の数のほうが少なくなるはずです。小さなゴミ・影を除いた、本物の塊の数が `len(clumps)` です。

> **やってみよう 1**
> `MIN_LEAF_AREA` を `600 → 50` に下げると、ふるった後の塊の数はどうなるでしょうか? 予想してから実行してください。しきい値を下げるほど、小さなノイズまで「塊」として数えてしまうことを確認しましょう。

この `MIN_LEAF_AREA` が、`leaf_monitor.py` の同名の設定です。塊数（clumps）の数え方を決める、大事なつまみです。

---

## 6.5 凸包（convexHull）：バラバラを1つにまとめる

ここが `leaf_monitor.py` のいちばん賢いところの1つです。

マットの上には鉢が置かれています。すると、鉢に隠れてマットが**いくつかの断片に分断**されて見えることがあります。マット色のマスクを取ると、1枚のマットなのに、左・右・上…と複数の白い島に分かれてしまうのです。

でも私たちが知りたいのは「マット全体の外形」です。バラバラの断片を、**1つの大きな外形にまとめたい**。そこで使うのが **凸包（convex hull・とつぼう）** です。

凸包は、「散らばった点すべてを、外側からピンと張った輪ゴムで囲んだときの形」だと思ってください。へこみのない、全体を包む最小の多角形ができます。

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

`np.vstack(pts)` は、複数の断片の点を**縦に積み重ねて1つにまとめる**NumPy の操作です。そうしてまとめた全部の点を `cv2.convexHull` に渡すと、それらを囲む1つの外形が返ってきます。これで「分断されたマット」が「1つのマット外形」に復元されました。

`MIN_MAT_FRAGMENT`（既定2000）は、「これより小さい白い島は、マットの断片とは認めず無視する」というしきい値です。小さな緑のゴミなどを、うっかりマットに含めないための予防線です。

---

## 6.6 fillPoly：外形を塗りつぶしてマスクにする

凸包はまだ「ふちどり（線）」です。これを計測に使うには、内部を白く塗りつぶして**マスク**にする必要があります。`cv2.fillPoly` を使います。

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

`np.zeros(mat.shape, dtype=np.uint8)` で、まず**真っ黒な台紙**を用意します（第0章のおさらいですね）。そこに `cv2.fillPoly` で凸包の内部を白く塗ります。

`mat_region.jpg` を VS Code で開くと、鉢で分断されていたマットが、**穴のない1枚の白い領域**になっているはずです。これが「マット全体の外形」のマスクで、`leaf_monitor.py` の `region.png` のもとになります。

> **やってみよう 2**
> `mat_mask.jpg`（分断されている）と `mat_region.jpg`（凸包で埋めた）を見比べてください。凸包が「断片のすき間」までまとめて1つにしていることが分かります。この後、ここから鉢を除けば、いよいよ計測範囲が完成します（第7章）。

---

## 6.7 `leaf_monitor.py` への橋渡し

この章の道具は、`mat_region_from_mask()` という関数にまとまって登場します。

```python
def mat_region_from_mask(mat_color):
    cnts, _ = cv2.findContours(mat_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pts = [c for c in cnts if cv2.contourArea(c) >= MIN_MAT_FRAGMENT]
    ...
    hull = cv2.convexHull(np.vstack(pts))
    region = np.zeros(mat_color.shape, dtype=np.uint8)
    cv2.fillPoly(region, [hull], 255)
    return region
```

`step16.py`〜`step19.py` でやったことが、ほぼそのままこの1つの関数になっています。「輪郭を取る → 大きい断片だけ残す → 凸包でまとめる → 塗りつぶしてマスクにする」という、この章の流れそのものです。仕様書 7.4 が説明している「鉢でマットが分断されていても、断片をまとめて1つのマット範囲として復元できる」が、ここで実現されています。

また、塊を数える側では `analyze()` に次の行があります。

```python
leaf_cnts, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clumps = [c for c in leaf_cnts if cv2.contourArea(c) >= MIN_LEAF_AREA]
```

`step16.py`〜`step17.py` の「輪郭を取って面積でふるう」が、堆積物の塊を数えるのに使われています。

---

## 6.8 この章のまとめ

- **輪郭（contour）** は白い領域のふちどり。塊を数えたり面積を測ったりするのに使う。
- `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)` で外側の輪郭だけを軽く取り出す。
- `cv2.contourArea` で面積を測り、小さい輪郭（ノイズ）をふるい落とせる（`MIN_LEAF_AREA`・`MIN_MAT_FRAGMENT`）。
- `cv2.convexHull` は、散らばった点を輪ゴムで囲った外形（凸包）を作る。分断されたマットを1つにまとめる。
- `cv2.fillPoly` で、その外形の内部を白く塗ってマスクにする。

---

## 6.9 確認問題

1. `cv2.findContours` の引数 `cv2.RETR_EXTERNAL` は、どんな輪郭を取り出す指定か説明しなさい。
2. 影やノイズによる小さな塊を「数えない」ようにするには、どの関数で何を調べ、どう判定すればよいか説明しなさい。
3. 鉢でマットが3つの白い島に分断されてしまった。これを1つのマット外形にまとめるには、どの関数を使うか答えなさい。また、その関数のイメージを「輪ゴム」を使って説明しなさい。
4. 凸包は「ふちどり（線）」のままでは計測に使えない。マスクにするために何をするか、使う関数とともに答えなさい。

---

**次章予告 ── 第7章「面積を測る（被覆面積率）」**
マット全体の外形ができました。ここから鉢を除けば「固定の計測範囲」が完成します。次章では、白い画素を数える `cv2.countNonZero` を使って、いよいよ `leaf_monitor.py` の主役の指標「**被覆面積率（％）**」を計算します。なぜ計測範囲を毎回作り直さず固定するのか、その理由もはっきりします。
