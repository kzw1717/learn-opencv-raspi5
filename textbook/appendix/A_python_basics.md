# 付録A Pythonの構文・型・ライブラリ一覧

> このテキストの step スクリプトと `leaf_monitor.py` で使われている **Python の構文・データ型・ライブラリ**を、OpenCV の機能とは別の切り口で整理した早見表です。
> 「この書き方、なんだっけ？」と思ったときの逆引きに使ってください。各項目に、実際のコードからの例を添えています。

---

## A.1 制御構文・文（プログラムの骨組み）

| 構文 | 役割 | 実例（出典） |
|---|---|---|
| `import` / `from … import` | ライブラリを読み込む | `import cv2` / `from datetime import datetime`（leaf_monitor.py） |
| `def`（関数定義） | 処理に名前を付けてまとめる | `def analyze(img_bgr, lower, upper, region, pot):`（leaf_monitor.py） |
| `return` | 関数から値を返す | `return coverage_pct, len(clumps), annotated`（analyze） |
| `if` / `elif` / `else` | 条件で処理を分ける | `if lower[0] < 0:` … `if upper[0] > 180:`（get_mat_mask） |
| `while`（くりかえし） | 条件が真の間くりかえす | `while True:`（main の `--loop` ループ） |
| `for`（くりかえし） | 並んだものを順に処理する | `for name in ["mat_bright.jpg", "mat_dark.jpg"]:`（step7） |
| `try` / `except` | エラーを捕まえて対処する | `try: from picamera2 import Picamera2 / except ImportError:`（capture_image） |
| `with`（コンテキストマネージャ） | ファイルなどを安全に開閉する | `with open(LOG_CSV, "a", newline="") as f:`（append_log） |
| `if __name__ == "__main__":` | 直接実行されたときだけ動かす | スクリプト末尾（leaf_monitor.py） |

### くわしく：いくつかの構文

**`while True:` と「無限ループの止め方」**
`leaf_monitor.py` の `--loop` は、`while True:`（ずっと真）で計測をくりかえします。止めるのは Ctrl+C で、それを `try` / `except KeyboardInterrupt` で受け止めて、きれいに終了します。

```python
try:
    while True:
        run_once()
        time.sleep(args.loop)
except KeyboardInterrupt:
    print("\n停止しました。")
```

**`try` / `except` は「保険」**
`capture_image()` では、カメラ用ライブラリが入っていない環境でも分かりやすく終われるよう、読み込みを `try` で囲み、失敗（`ImportError`）したらインストール方法を表示して終了します。

**`with open(...)` は「閉じ忘れ防止」**
ファイルを開いたら必ず閉じる必要がありますが、`with` を使うとブロックを抜けるとき自動で閉じてくれます。CSV や JSON の読み書きで使われています。

---

## A.2 式・便利な書き方

| 書き方 | 役割 | 実例 |
|---|---|---|
| 多重代入（タプルアンパック） | 複数の変数に一度に代入 | `Hc, Sc, Vc = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]`（calibrate） |
| `_`（捨て変数） | 使わない戻り値を受け流す | `cnts, _ = cv2.findContours(...)`（mat_region_from_mask） |
| リスト内包表記 | 条件に合う要素だけ集めて新しいリストに | `clumps = [c for c in leaf_cnts if cv2.contourArea(c) >= MIN_LEAF_AREA]`（analyze） |
| 条件式（三項演算子） | `A if 条件 else B` を1行で | `coverage_pct = 100.0 * leaf_area / region_area if region_area else 0.0`（analyze） |
| f文字列（f-string） | 文字列に変数を埋め込む | `f"[{ts}] 被覆面積率={coverage:.2f}%  塊数={clumps}"`（run_once） |
| フォーマット指定 | 桁数や形式を整える | `:.2f`（小数2桁）、`:.3f`（小数3桁）、`%H%M%S`（日時） |
| キーワード引数 | 引数を名前で渡す | `iterations=1`、`indent=2`、`exist_ok=True`、`minlength=180` |

### くわしく：リスト内包表記

`leaf_monitor.py` で何度も出てくる、とても Python らしい書き方です。「全部の輪郭のうち、面積が一定以上のものだけ集める」を1行で書いています。

```python
# 「c を順に見て、面積が MIN_LEAF_AREA 以上の c だけ集める」
clumps = [c for c in leaf_cnts if cv2.contourArea(c) >= MIN_LEAF_AREA]
```

ふつうの `for` 文で書くと次と同じ意味です。内包表記のほうが短く読みやすくなります。

```python
clumps = []
for c in leaf_cnts:
    if cv2.contourArea(c) >= MIN_LEAF_AREA:
        clumps.append(c)
```

---

## A.3 データ型（値の種類）

| 型 | 説明 | 実例 |
|---|---|---|
| `int`（整数） | 整数 | `H_MARGIN = 12`、`peak`、`region_area` |
| `float`（小数） | 小数 | `SETTLE_SEC = 2.0`、`coverage_pct`、`100.0 * ...` |
| `str`（文字列） | 文字の並び | `"mat_config.json"`、`ts`（日時文字列） |
| `bool`（真偽値） | `True` / `False` | `args.calibrate`、`new_file = not os.path.exists(...)` |
| `None`（値なし） | 「無い」を表す特別な値 | `pot = ... if os.path.exists(...) else None` |
| `list`（リスト） | 順番のある入れもの。`[ ]` | `lower = [peak - H_MARGIN, ...]`、`pts`、`clumps` |
| `tuple`（タプル） | 変更できない並び。`( )` | `RESOLUTION = (2028, 1520)`、`(5, 5)` |
| `dict`（辞書型） | 「名前→値」の対応表。`{ }` | `json.dump({"lower": lower, "upper": upper, ...})`（calibrate） |
| `numpy.ndarray` | 数字の表（画像・マスクの正体） | `img`、`hsv`、`mask`、`region` |
| ファイルオブジェクト | 開いたファイルを表す | `open(...) as f` の `f` |

### くわしく：リスト・タプル・辞書の使い分け

- **リスト `[ ]`** … あとから中身を増減・変更したいときの入れもの。HSV の下限 `lower = [H, S, V]` など。
- **タプル `( )`** … 変えたくない・変わらない組。解像度 `(2028, 1520)` やカーネルサイズ `(5, 5)` など。
- **辞書 `{ }`** … 「キー（名前）」で値を取り出したいとき。`leaf_monitor.py` はマット色設定を辞書にして JSON 保存し、読み込み時に `cfg["lower"]` のようにキーで取り出します。

```python
# 保存（辞書 → JSON ファイル）
json.dump({"lower": lower, "upper": upper, "peak_hue": peak}, f, indent=2)

# 読み込み（JSON ファイル → 辞書）→ キーで取り出す
cfg = json.load(f)
return np.array(cfg["lower"]), np.array(cfg["upper"])
```

### くわしく：`None` の使いみち

`run_once()` では、鉢マスクのファイルが無いこともあるので、「無ければ `None`」としておき、後で `if pot is not None:` のように存在を確認してから使います。「値が無い状態」をきちんと扱うための型です。

```python
pot = cv2.imread(POT_MASK, cv2.IMREAD_GRAYSCALE) if os.path.exists(POT_MASK) else None
```

---

## A.4 配列（並んだデータ）── リスト・タプル・NumPy配列

**配列**とは、ひとことで言うと「**同じような値を順番に並べた入れもの**」です。並んでいるので、**番号（インデックス）で1つずつ取り出せる**のが最大の特徴です。番号は **0 から始まる**点に注意してください（1番目は `[0]`、2番目は `[1]`）。

Python で「並んだデータ」を表すものには、大きく次の種類があります。

| 種類 | 次元 | 中身を変えられる？ | 主な用途・実例 |
|---|---|---|---|
| `list`（リスト）`[ ]` | 1次元（1列に並ぶ） | 変えられる | `lower = [peak - H_MARGIN, ...]`（HSVの下限） |
| `tuple`（タプル）`( )` | 1次元（1列に並ぶ） | 変えられない | `RESOLUTION = (2028, 1520)`、カーネル `(5, 5)` |
| `numpy.ndarray` | 多次元（表・立体） | 変えられる | `img`・`hsv`・`mask`（画像とマスクの正体） |

`list` と `tuple` は「1列に並んだデータ」、NumPy の `ndarray` は「**縦横に広がった数字の表**」だと思ってください。画像は色の数字が縦横にびっしり並んだ表なので、自然と NumPy の多次元配列になります（→ 第1章）。

### くわしく：番号で取り出す（インデックスとスライス）

並んでいるからこそ、番号で取り出せます。1次元（list）と多次元（画像）で、取り出し方の見た目が変わります。

```python
# 1次元のリスト：番号は0から
lower = [120, 170, 190]
print(lower[0])     # 120（1番目）
print(lower[2])     # 190（3番目）

# 多次元のNumPy配列（画像）：行と列を指定
print(img[100, 200])      # 上から100・左から200の画素（BGRの3つ組）
print(img[100, 200][2])   # その画素の赤(R)。BGRなので3つ目
```

「`:`（コロン）」を使って、範囲をまとめて取り出すのが**スライス**です。画像の色チャンネルを抜き出すときに活躍します。

```python
h = hsv[:, :, 0]   # 全部の行・全部の列の、0番目（色相H）だけを取り出す
img[:, :, ::-1]    # 3つ組の並びを逆さに（BGR↔RGB、step3 の色を壊す実験）
```

### くわしく：何次元か＝shape で分かる

配列が「1列なのか・表なのか・立体なのか」は、`.shape`（形）を見れば分かります。これは第1章で出てきた考え方そのものです。

| データ | shape の例 | 意味 |
|---|---|---|
| リスト `[120, 170, 190]` | `(3,)` | 1次元（3個並ぶ） |
| 白黒マスク | `(1520, 2028)` | 2次元（縦×横） |
| カラー画像 | `(1520, 2028, 3)` | 3次元（縦×横×色3つ） |

### なぜ配列で扱うのか

画像の画素は何百万個もあります。これを1つずつ `for` 文で処理すると、とても遅くなります。配列（特に NumPy）でまとめて持てば、「全部の画素を一気に計算する」「条件に合う画素だけまとめて選ぶ」といった操作が、短く・速く書けます。`leaf_monitor.py` がマットの色をまとめて学習できるのも、画像を配列として扱っているからです。配列を作る・形を調べる・条件で選ぶといった具体的な機能は、後ろの「**A.8 NumPy で使われている機能**」で詳しくまとめています。

> **ひとことメモ**：このあとに出てくる「オブジェクト」とのつながり——NumPy 配列は「配列」であると同時に「オブジェクト」でもあり、`.shape`（属性）や `.copy()`（メソッド）を持ちます。まず「番号で取り出せる並んだデータ＝配列」を押さえ、次の節で「属性とメソッドを持つもの＝オブジェクト」を見ていきます。

---

## A.5 オブジェクトとメソッド（オブジェクト指向の使われ方）

`leaf_monitor.py` は自分で**クラスを定義してはいません**が、ライブラリが用意したクラスから**オブジェクト（実体）**を作って使っています。この「オブジェクト指向の利用者側」の使い方を押さえましょう。

| 概念 | 説明 | 実例 |
|---|---|---|
| インスタンス化 | クラスから実体（オブジェクト）を作る | `picam2 = Picamera2()`、`parser = argparse.ArgumentParser(...)` |
| メソッド呼び出し | オブジェクトに付いた関数を呼ぶ | `picam2.configure(config)`、`picam2.start()`、`picam2.capture_file(path)` |
| 属性アクセス | オブジェクトが持つ値を `.` で取り出す | `args.calibrate`、`args.loop`、`img.shape`、`img.dtype` |

### くわしく：カメラオブジェクトの一生

`capture_image()` では、カメラを表すオブジェクトを作り、設定し、起動し、撮り、止め、閉じる——という一連のメソッドを順に呼んでいます。「もの（オブジェクト）に動作（メソッド）を命じる」のがオブジェクト指向の使い方です。

```python
picam2 = Picamera2()                                   # 実体を作る
config = picam2.create_still_configuration(...)         # メソッドで設定を作る
picam2.configure(config)                                # 設定を適用
picam2.start()                                          # 起動
picam2.capture_file(path)                               # 撮影して保存
picam2.stop()                                           # 停止
picam2.close()                                          # 後始末
```

### くわしく：NumPy 配列もオブジェクト

画像（NumPy 配列）も、`.shape`・`.dtype` という**属性**や、`.astype()`・`.ravel()`・`.copy()` という**メソッド**を持つオブジェクトです。

```python
print(img.shape)              # 属性：形
print(img.dtype)              # 属性：数字の種類
annotated = img_bgr.copy()    # メソッド：複製を作る
Hc.astype(int)                # メソッド：型を変える
Hc[valid].ravel()             # メソッド：1次元に平らにする
```

---

## A.6 標準ライブラリ（Python に最初から付いてくる道具）

`leaf_monitor.py` が使っている標準ライブラリです。`pip` や `apt` でのインストールは不要です。

| ライブラリ | 役割 | 使われ方の例 |
|---|---|---|
| `os` | ファイルパス・フォルダ操作 | `os.path.join(...)`、`os.path.exists(...)`、`os.makedirs(..., exist_ok=True)` |
| `sys` | プログラムの制御 | `sys.exit("…")`（メッセージを出して終了） |
| `time` | 時間まわり | `time.sleep(SETTLE_SEC)`（指定秒待つ） |
| `datetime` | 日時の取得・整形 | `datetime.now().strftime("%Y%m%d_%H%M%S")`（撮影時刻を文字列に） |
| `json` | JSON の読み書き | `json.dump(...)` / `json.load(...)`（マット色設定の保存・読込） |
| `csv` | CSV の読み書き | `csv.writer(f)`、`w.writerow([...])`（ログ追記） |
| `argparse` | コマンドライン引数の解釈 | `--calibrate`、`--loop 3600` などを解釈 |

### くわしく：argparse の流れ

`main()` は、`--calibrate` や `--loop` といったコマンドラインの指定を `argparse` で読み取り、`args` オブジェクトの属性として受け取ります。

```python
parser = argparse.ArgumentParser(description="…")
parser.add_argument("--calibrate", action="store_true", help="…")  # 付けたらTrueになるスイッチ
parser.add_argument("--loop", type=int, metavar="SEC", help="…")    # 数値を受け取る
args = parser.parse_args()

if args.calibrate:      # スイッチが付いていれば
    calibrate()
```

- `action="store_true"` … その引数が付いていれば `True`、なければ `False`。
- `type=int` … 受け取った値を整数に変換する。

---

## A.7 外部ライブラリ（別途インストールが必要な道具）

| ライブラリ | 別名 | 役割 | 導入方法 |
|---|---|---|---|
| OpenCV | `cv2` | 画像処理の主役（本テキスト第1〜8章） | `sudo apt install python3-opencv` |
| NumPy | `np` | 数字の表（配列）の計算 | `sudo apt install python3-numpy` |
| picamera2 | （`Picamera2`） | Raspberry Pi のカメラ撮影 | `sudo apt install python3-picamera2` |

OpenCV の関数（`cv2.imread`・`cv2.inRange` など）については、第1〜8章および前回の関数一覧で詳しく扱っています。ここでは「外部ライブラリの1つ」という位置づけだけ確認しておきます。

> **メモ：`import cv2` なのにライブラリ名は OpenCV**
> インストール名（`python3-opencv`）・読み込み名（`cv2`）・通称（OpenCV）が食い違うので、最初は戸惑います。「画像処理 ＝ OpenCV ＝ `import cv2`」とセットで覚えてしまいましょう。NumPy は慣習で `import numpy as np` と短い別名を付けて使います。

---

## A.8 NumPy で使われている機能（くわしめ）

画像処理は NumPy 抜きには語れないので、`leaf_monitor.py` と step スクリプトで登場する NumPy 機能を、もう少し細かく整理します。

### 配列を作る

| 機能 | 役割 | 実例 |
|---|---|---|
| `np.array([...])` | リストから配列を作る | `np.array(cfg["lower"])`（load_mat_config） |
| `np.zeros(形, dtype=np.uint8)` | すべて0（真っ黒）の配列を作る | `region = np.zeros(mat_color.shape, dtype=np.uint8)`（mat_region_from_mask） |
| `np.vstack([...])` | 複数の配列を縦に積み重ねて1つに | `cv2.convexHull(np.vstack(pts))`（mat_region_from_mask） |
| `np.uint8` | 0〜255の整数という型の指定 | `dtype=np.uint8`、`upper.astype(np.uint8)` |

### 形・型を調べる／変える

| 機能 | 役割 | 実例 |
|---|---|---|
| `.shape` | 配列の形（縦・横・色数） | `img.shape` → `(1520, 2028, 3)` |
| `.dtype` | 1マスの数字の種類 | `img.dtype` → `uint8` |
| `.astype(型)` | 型を変える | `Hc.astype(int)`（calibrate） |
| `.ravel()` | 多次元配列を1次元に平らにする | `Hc[valid].ravel()`（calibrate） |

### 取り出す（スライス・インデックス）

| 書き方 | 役割 | 実例 |
|---|---|---|
| `arr[行, 列]` | 1点を取り出す | `img[100, 200]`、`hsv[760, 1000]` |
| `arr[:, :, 0]` | 3つ組のうち0番目だけ取り出す | `hsv[:, :, 0]`（色相だけ） |
| `arr[:, :, ::-1]` | 並びを逆さにする | `img[:, :, ::-1]`（BGR↔RGB、step3） |
| 真偽配列インデックス | 条件に合う画素だけ取り出す | `Sc[matpix]`、`Vc[matpix]`（calibrate） |

### 条件・集計の計算（calibrate の色学習で活躍）

| 機能 | 役割 | 実例 |
|---|---|---|
| 比較で真偽配列を作る | 各画素が条件に合うかを一括判定 | `valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)` |
| `&` / `\|` | 真偽配列やマスクの「かつ」「または」 | `matpix = valid & (hue_dist <= H_MARGIN)` |
| `np.count_nonzero(...)` | 真（0でない）の数を数える | `if np.count_nonzero(valid) < 1000:` |
| `np.bincount(..., minlength=180)` | 値ごとの個数を数える（ヒストグラム） | 色相ごとの画素数を集計 |
| `np.argmax(...)` | 最大値の位置（＝最頻色相）を返す | `peak = int(np.argmax(np.bincount(...)))` |
| `np.median(...)` | 中央値を求める | `s_med, v_med = int(np.median(Sc[matpix])), ...` |
| `np.abs(...)` / `np.minimum(...)` | 絶対値／2つの小さいほう | 色相の距離計算 `hue_dist = np.minimum(...)` |

### くわしく：真偽配列でまとめて選び出す

`calibrate()` の色学習は、NumPy の「真偽配列インデックス」が主役です。「彩度が十分・明るすぎず暗すぎない画素」を一括で `True/False` の表にし、その `True` の画素だけを取り出して、マットの代表色を求めています。`for` 文で1画素ずつ回さず、配列まるごと一気に処理するのが NumPy らしさです。

```python
# 各画素が条件に合うかを True/False の配列で一括判定
valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)

# True の画素の色相だけ集めて、いちばん多い色相＝マット色を求める
peak = int(np.argmax(np.bincount(Hc[valid].ravel(), minlength=180)))
```

---

## A.9 全体まとめ（カテゴリ早見）

- **制御構文**：`import` / `def` / `return` / `if`-`elif`-`else` / `while` / `for` / `try`-`except` / `with` / `if __name__ == "__main__":`
- **便利な記法**：多重代入・`_`捨て変数・リスト内包表記・条件式（三項演算子）・f文字列・キーワード引数
- **データ型**：`int` / `float` / `str` / `bool` / `None` / `list` / `tuple` / `dict` / `numpy.ndarray` / ファイルオブジェクト
- **配列（並んだデータ）**：`list`・`tuple`（1次元）と `numpy.ndarray`（多次元＝画像・マスク）。番号（0始まり）やスライスで取り出す。`shape` で次元が分かる。
- **オブジェクトの使い方**：インスタンス化・メソッド呼び出し・属性アクセス（自前のクラス定義はなし）
- **標準ライブラリ**：`os` / `sys` / `time` / `datetime` / `json` / `csv` / `argparse`
- **外部ライブラリ**：`cv2`（OpenCV）/ `numpy` / `picamera2`
- **NumPy**：配列生成（`array`/`zeros`/`vstack`）・形と型（`shape`/`dtype`/`astype`/`ravel`）・スライスと真偽配列インデックス・集計（`bincount`/`argmax`/`median`/`count_nonzero` など）

`leaf_monitor.py` は、特別に難しい文法は使っていません。**高校情報で学ぶ基本構文（条件分岐・くりかえし・関数）に、リスト内包表記・辞書・例外処理・NumPy 配列を少し足しただけ**で成り立っています。一つひとつは、このテキストの step スクリプトで手を動かしてきたものばかりです。
