# 第8章 結果を描く（可視化）

> 被覆面積率と塊数という「数字」は出せました。
> でも、その検出が本当に正しいのか、人の目で確かめたいですよね。
> この章では、もとの写真の上に検出結果を描き込んで、第0章で予告した「あの確認画像」をついに完成させます。

---

## 8.1 この章のゴール

この章を終えると、次のことができるようになります。

- なぜ「人が目で確認できる画像」を作るのかを説明できる
- `cv2.drawContours` で、輪郭を好きな色・太さで描ける
- `cv2.putText` で、画像に文字（数値）を書き込める
- 色を指定するとき、再び **BGR の順番** に注意する必要があることを思い出せる
- `leaf_monitor.py` の annotated 画像がどう作られているか、完全に理解できる

---

## 8.2 なぜ「確認画像」を作るのか

`leaf_monitor.py` は無人で動き続けます。だからこそ、「ちゃんと正しく検出できているか」を後から人間がチェックできる仕組みが要ります。数字だけ見ても、「12.34%」が正しいのか、影を誤検出した結果なのかは分かりません。

そこで、もとの写真の上に「どこを計測範囲とみなし、どこを鉢として除外し、どこを堆積物として検出したか」を**色分けして描き込んだ画像**を作ります。これが annotated 画像です。これを見れば、「青線（範囲）が変な所まで広がっていないか」「緑線（堆積物）が影を拾っていないか」が一目で分かります。仕様書のトラブルシューティングでも、調整のたびにこの画像を見て確認するよう繰り返し勧めています。

---

## 8.3 drawContours で輪郭を描く

`cv2.drawContours` は、輪郭（ふちどり）を画像の上に線で描く関数です。第6章で取り出した輪郭を、もとの写真に重ねてみましょう。

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

`cv2.drawContours` の引数を見ていきます。

- `annotated` … 描き込む先の画像（もとの写真のコピー）。
- `contours` … 描きたい輪郭のリスト。
- `-1` … 「リストの**全部**の輪郭を描く」という意味（特定の1本だけ描きたいなら 0, 1, … と番号を指定）。
- `(0, 255, 0)` … 線の色。**ここが要注意です**（次の節）。
- `2` … 線の太さ（ピクセル）。

> `img.copy()` でコピーに描いているのは、もとの `img` を壊さないためです。元画像はそのまま取っておきたいので、描画は必ずコピーに対して行います。

---

## 8.4 ふたたびBGRの罠：色の順番

`(0, 255, 0)` が緑になるのはなぜでしょうか。第1章を思い出してください。**OpenCV の色は BGR（青・緑・赤）の順**でした。色の指定もこの順番です。

- `(255, 0, 0)` → **青**（Blueが255）
- `(0, 255, 0)` → **緑**（Greenが255）
- `(0, 0, 255)` → **赤**（Redが255）
- `(0, 255, 255)` → **黄**（GreenとRedが255。緑＋赤＝黄）

「赤を描きたくて `(255, 0, 0)` と書いたら青になった」——これは初心者が必ず一度はやる失敗です。第1章で学んだ BGR の順番が、描画でもそのまま効いてくるわけです。

`leaf_monitor.py` の色分けも、この BGR で決まっています。

- 計測範囲：`(255, 0, 0)` ＝ **青**
- 鉢（除外）：`(0, 255, 255)` ＝ **黄**
- 堆積物：`(0, 255, 0)` ＝ **緑**

> **やってみよう 1**
> `step22.py` の `(0, 255, 0)` を `(0, 0, 255)` に変えて実行し、落ち葉の囲み線が**赤**になることを確認しましょう。次に `(255, 0, 0)` にすると青になります。BGR の順番を体で覚えてください。

---

## 8.5 putText で数値を書き込む

最後に、被覆面積率と塊数を画像の中に文字で書き込みます。`cv2.putText` を使います。

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

`cv2.putText` の引数です。

- `annotated` … 書き込む先の画像。
- `label` … 書き込む文字列。
- `(10, 30)` … 文字を書き始める位置（左から10、上から30）。
- `cv2.FONT_HERSHEY_SIMPLEX` … フォントの種類（OpenCV に用意された定番フォント）。
- `1.0` … 文字の大きさ。
- `(0, 0, 255)` … 文字の色。BGR なので、これは**赤**です。
- `2` … 文字の線の太さ。

`annotated_full.jpg` を VS Code で開いてください。落ち葉が緑で囲まれ、左上に `coverage=...%  clumps=...` と赤い文字で表示された、**第0章で予告した確認画像**ができあがっているはずです。ここがこのテキストの1つのゴール地点です。

> **やってみよう 2**
> `step23.py` に、計測範囲を青で、（もしあれば）鉢を黄で描く `drawContours` を追加して、`leaf_monitor.py` と同じ「青・黄・緑」の3色がそろった確認画像を作ってみましょう。

---

## 8.6 `leaf_monitor.py` への橋渡し

この章の描画は、`analyze()` の後半にまとまっています。

```python
annotated = img_bgr.copy()
rcnts, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(annotated, rcnts, -1, (255, 0, 0), 2)        # 計測範囲: 青
if pot is not None:
    pcnts, _ = cv2.findContours(pot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(annotated, pcnts, -1, (0, 255, 255), 2)  # 除外(鉢): 黄
cv2.drawContours(annotated, clumps, -1, (0, 255, 0), 2)       # 落ち葉: 緑
label = f"coverage={coverage_pct:.2f}%  clumps={len(clumps)}"
cv2.putText(annotated, label, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
```

`step22.py`〜`step23.py` でやったことが、ほぼそのまま並んでいます。`img_bgr.copy()` でコピーに描くこと、BGR の色指定（青=範囲、黄=鉢、緑=堆積物、赤い文字）、`FONT_HERSHEY_SIMPLEX` での文字描画——すべて、この章で学んだとおりです。

そして、こうして作った annotated 画像は `run_once()` の中で `cv2.imwrite(ann_path, annotated)` として保存され（第1章）、後で `scp` などで PC に持ってきて目視確認する、という運用につながります（第10章）。

---

## 8.7 この章のまとめ

- 無人で動くシステムだからこそ、人が後で確認できる**色分けの確認画像（annotated）**を作る。
- `cv2.drawContours(画像, 輪郭, -1, 色, 太さ)` で輪郭を描く。`-1` は「全部の輪郭」。
- `cv2.putText(画像, 文字, 位置, フォント, 大きさ, 色, 太さ)` で数値などを書き込む。
- 色は再び **BGR** 順。青=`(255,0,0)`・緑=`(0,255,0)`・赤=`(0,0,255)`・黄=`(0,255,255)`。
- もとの画像を壊さないよう、描画は `img.copy()` に対して行う。

---

## 8.8 確認問題

1. `cv2.drawContours` の第3引数に `-1` を渡すと、どの輪郭が描かれるか答えなさい。
2. OpenCV で「赤い線」を描きたい。色の指定 `(?, ?, ?)` を、BGR の順番に注意して書きなさい。
3. 描画するとき、もとの画像そのものではなく `img.copy()` に描くのはなぜか説明しなさい。
4. `leaf_monitor.py` の確認画像で、青・黄・緑の線がそれぞれ何を表しているか答えなさい。

---

**次章予告 ── 第9章「leaf_monitor.py を通して読む」**
ここまでで、`leaf_monitor.py` に出てくる OpenCV の道具をすべて学びました。次章では、いよいよ本物のコードを頭から通して読み、一つひとつの `cv2.〇〇()` を「これは○章でやったやつだ」と回収していきます。バラバラに学んだ道具が、1本のプログラムとしてつながる瞬間です。
