# 第9章 leaf_monitor.py を通して読む

> ここまでで、`leaf_monitor.py` に出てくる OpenCV の道具をすべて学びました。
> この章では、本物のコードを頭から通して読み、一つひとつの `cv2.〇〇()` を「これは○章でやったやつだ」と回収していきます。
> バラバラに学んだ道具が、1本のプログラムとしてつながる瞬間です。

---

## 9.1 この章のゴール

この章を終えると、次のことができるようになります。

- `leaf_monitor.py` の全体の流れ（2つのモード）を説明できる
- 各 OpenCV 関数が、どの章で学んだ何にあたるかを言える
- 「キャリブレーション」と「計測」がどう役割分担しているか理解できる
- このテキストの最終ゴール「OpenCV をすべて自分の言葉で説明できる」に到達する

---

## 9.2 まず全体像：2つのモードがある

`leaf_monitor.py` には、大きく2つの動き方があります。

**(A) キャリブレーション（`--calibrate`）= 最初の準備**
落ち葉のない、きれいな状態を1回撮影し、「マットの色」「鉢の場所」「固定の計測範囲」を学習・保存します。最初に1回、そしてマットや鉢、照明、カメラ位置を変えたら、そのつど行います。

**(B) 計測（引数なし、または `--loop`）= ふだんの仕事**
保存しておいた設定を読み込み、写真を撮って被覆面積率を計算し、ログと確認画像を残します。cron などで定期的に繰り返します。

この2つは、**ここまで学んだ同じ道具を、違う順番・違う目的で組み合わせている**だけです。順に見ていきましょう。

---

## 9.3 関数と「学んだ章」の対応表

まず、`leaf_monitor.py` に登場する OpenCV 関数の一覧と、対応する章を整理します。これがこのテキスト全体の地図です。

| OpenCV 関数 | 役割 | 学んだ章 |
|---|---|---|
| `cv2.imread` | 画像・マスクをファイルから読む | 第1章 / 第7章 |
| `cv2.imwrite` | 画像・マスクをファイルに保存する | 第1章 |
| `cv2.cvtColor`（BGR2HSV） | HSV に変換する | 第2章 |
| `cv2.inRange` | 色の範囲を白く抜き出す（マスク作成） | 第3章 |
| `cv2.getStructuringElement` | モルフォロジー用のブラシを作る | 第4章 |
| `cv2.morphologyEx`（OPEN/CLOSE） | ノイズ消し・穴埋め | 第4章 |
| `cv2.dilate` | 白い領域を太らせる（鉢の縁対策） | 第4章 |
| `cv2.bitwise_not` | 白黒を反転（「〜でない」） | 第5章 |
| `cv2.bitwise_and` | 重なりだけ残す（「かつ」） | 第5章 |
| `cv2.findContours` | 輪郭（ふちどり）を取り出す | 第6章 |
| `cv2.contourArea` | 輪郭の面積を測る | 第6章 |
| `cv2.convexHull` | 断片を1つの外形にまとめる（凸包） | 第6章 |
| `cv2.fillPoly` | 外形の内部を塗ってマスクにする | 第6章 |
| `cv2.countNonZero` | 白い画素を数える（面積） | 第7章 |
| `cv2.drawContours` | 輪郭を線で描く | 第8章 |
| `cv2.putText` | 画像に文字を書く | 第8章 |

15個の関数すべてに、対応する章があります。もう知らない関数は1つもありません。

---

## 9.4 キャリブレーションを読む（calibrate）

`calibrate()` を、コードの流れに沿って読みます。

**① 撮影して読み込む（第1章）**

```python
capture_image(path)
img = cv2.imread(path)
```

落ち葉のない状態を撮り、数字の表として読み込みます。

**② HSV に変換し、3つに分ける（第2章）**

```python
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
Hc, Sc, Vc = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
```

色味で判断するため HSV にし、H・S・V を取り出します。このあと、最も面積を占める色相（H）を「マットの色」と判断します。

**③ マットの色範囲を決めてマスクを作る（第3章）**

```python
lower = [peak - H_MARGIN, ...]
upper = [peak + H_MARGIN, ...]
mat_color = get_mat_mask(hsv, np.array(lower), np.array(upper))   # 中で cv2.inRange
```

「代表色 ± マージン」で範囲を決め、`cv2.inRange` でマット色のマスクを作ります。

**④ マスクを掃除する（第4章）**

```python
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL, MORPH_KERNEL))
mat_color = cv2.morphologyEx(mat_color, cv2.MORPH_OPEN, k, iterations=1)
```

オープニングで小さなノイズを消します。

**⑤ マット外形を凸包でまとめる（第6章）**

```python
mat_region = mat_region_from_mask(mat_color)   # 中で findContours→contourArea→convexHull→fillPoly
```

鉢で分断されたマットを、1つの外形マスクに復元します。

**⑥ 鉢を取り出して太らせる（第5章・第4章）**

```python
pot = cv2.bitwise_and(mat_region, cv2.bitwise_not(mat_color))   # マット範囲 かつ マット色でない＝鉢
pot = cv2.morphologyEx(pot, cv2.MORPH_OPEN, k, iterations=2)
pot = cv2.dilate(pot, dk, iterations=1)                          # 縁の取りこぼし対策
cv2.imwrite(POT_MASK, pot)
```

落ち葉がないので、「マット範囲の中でマット色でないもの」は鉢です。少し太らせて保存します。

**⑦ 計測範囲を確定して固定保存（第5章・第7章）**

```python
region = cv2.bitwise_and(mat_region, cv2.bitwise_not(pot))   # マット範囲 から 鉢 を除く
cv2.imwrite(REGION_MASK, region)
```

マット外形から鉢を除いた領域が、固定の計測範囲です。`region.png` に保存し、以降のものさしにします。

これでキャリブレーション完了。`mat_config.json`（色範囲）・`pot.png`（鉢）・`region.png`（計測範囲）の3つが用意されました。

---

## 9.5 計測を読む（run_once → analyze）

次に、ふだんの計測 `run_once()` と、その中で呼ばれる `analyze()` を読みます。

**① 固定設定を読み戻す（第7章）**

```python
region = cv2.imread(REGION_MASK, cv2.IMREAD_GRAYSCALE)
pot = cv2.imread(POT_MASK, cv2.IMREAD_GRAYSCALE) if os.path.exists(POT_MASK) else None
```

キャリブレーションで保存した固定の計測範囲を、白黒で読み戻します。**毎回同じものさし**を使うのが肝でした。

**② 撮影して読み込む（第1章）**

```python
capture_image(cap_path)
img = cv2.imread(cap_path)
```

**③ HSV にしてマット色マスクを作り、掃除する（第2〜4章）**

```python
hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
mat_color = get_mat_mask(hsv, lower, upper)              # inRange
mat_color = cv2.morphologyEx(mat_color, cv2.MORPH_OPEN, k, iterations=1)
```

**④ 範囲の中でマット色でないもの＝堆積物を取り出す（第5章・第4章）**

```python
leaf_mask = cv2.bitwise_and(region, cv2.bitwise_not(mat_color))   # 範囲 かつ マット色でない
leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN,  k, iterations=1)
leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, k, iterations=2)
```

このテキストでいちばん大事にしてきた1行です。「範囲の中・マット色でない＝堆積物」。

**⑤ 面積を数えて被覆率を計算（第7章）**

```python
region_area = int(cv2.countNonZero(region))   # 固定なので毎回同じ
leaf_area   = int(cv2.countNonZero(leaf_mask))
coverage_pct = 100.0 * leaf_area / region_area if region_area else 0.0
```

**⑥ 塊を数える（第6章）**

```python
leaf_cnts, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clumps = [c for c in leaf_cnts if cv2.contourArea(c) >= MIN_LEAF_AREA]
```

**⑦ 確認画像を描く（第8章）**

```python
cv2.drawContours(annotated, rcnts,  -1, (255, 0, 0), 2)   # 範囲: 青
cv2.drawContours(annotated, pcnts,  -1, (0, 255, 255), 2) # 鉢: 黄
cv2.drawContours(annotated, clumps, -1, (0, 255, 0), 2)   # 堆積物: 緑
cv2.putText(annotated, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
```

**⑧ 保存・記録（第1章）**

```python
cv2.imwrite(ann_path, annotated)
append_log(ts, coverage, clumps)   # CSVに追記（OpenCVではない）
```

これで1回の計測が完了します。あとはこれを cron で繰り返すだけです。

---

## 9.6 全体を1つの流れとして眺める

最後に、計測1回ぶんの流れを通しで眺めてみましょう。

```
写真を読む（第1章）
  → HSVに変換（第2章）
    → マット色を抜き出す inRange（第3章）
      → ノイズを掃除する morphology（第4章）
        → 固定範囲 かつ マット色でない＝堆積物 bitwise（第5章）
          → 塊を輪郭で数える findContours/contourArea（第6章）
          → 白い画素を数えて被覆率 countNonZero（第7章）
            → 青・黄・緑と数値を描く drawContours/putText（第8章）
              → 保存して記録 imwrite（第1章）
```

第0章で見せた「一本道のパイプライン」が、本物のコードでそのまま動いていることが分かります。難しそうに見えた `leaf_monitor.py` は、ここまで一段ずつ学んできた素朴な道具の組み合わせにすぎなかったのです。

**おめでとうございます。** これでこのテキストの最終ゴール——「`leaf_monitor.py` の OpenCV をすべて自分の言葉で説明できる」——に到達しました。

---

## 9.7 この章のまとめ

- `leaf_monitor.py` には「キャリブレーション（準備）」と「計測（ふだんの仕事）」の2モードがある。
- 登場する OpenCV 関数15個は、すべてどこかの章で学んだもの。新しい道具はもう無い。
- キャリブレーションは「色学習→マット外形→鉢→固定範囲」を作って保存する。
- 計測は「固定範囲を読み戻し→堆積物抽出→被覆率→確認画像」を繰り返す。
- 全体は第0章のパイプラインそのもの。素朴な道具の積み重ねでできている。

---

## 9.8 確認問題（総合）

1. `leaf_monitor.py` の2つのモード（キャリブレーションと計測）の役割の違いを、それぞれ1〜2文で説明しなさい。
2. 計測時の「堆積物を取り出す1行」`cv2.bitwise_and(region, cv2.bitwise_not(mat_color))` が何をしているか、日本語で説明しなさい。
3. 被覆面積率の「分母（計測範囲）」が、計測のたびにファイルから読み戻されるのはなぜか説明しなさい。
4. 次の関数が「どの章で学んだ何か」を答えなさい：`cv2.cvtColor` / `cv2.inRange` / `cv2.morphologyEx` / `cv2.convexHull` / `cv2.countNonZero`。

---

**次章予告 ── 第10章「実際に運用する（発展）」**
OpenCV の理解は完成しました。最後の章では、学んだプログラムを実際に Raspberry Pi で動かし続けるための運用——キャリブレーションのコツ、cron での定期実行、確認画像の取り出し、チューニングの回し方——を、仕様書の内容とあわせて整理します。
