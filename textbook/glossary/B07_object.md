# 用語解説：オブジェクト

> `leaf_monitor.py` では、`picam2 = Picamera2()` でカメラの実体を作り、`picam2.start()` や `picam2.capture_file(path)` のように `.`（ドット）を付けて命令します。また `img.shape` や `img.copy()` のように、画像にもドットで何かを呼び出します。
> この「**ドットの前にあるもの**」が**オブジェクト**です。Python の世界では、ほとんどすべてがオブジェクトです。

---

## 1. これは何？（考え方）

オブジェクトは、ひとことで言うと

> **データ（属性）と、それにできる動作（メソッド）を、ひとまとめにしたもの**

です。身近な例で考えましょう。「スマホ」というオブジェクトには、

- **属性**（持っているデータ）：バッテリー残量、画面の明るさ…
- **メソッド**（できる動作）：電話をかける、写真を撮る…

があります。「スマホ.写真を撮る()」のように、「もの」に「動作」を命じる——これがオブジェクトの使い方です。

Python では、`.`（ドット）の使い方が2通りあります。

- `オブジェクト.属性` … 持っているデータを取り出す（例：`img.shape`）
- `オブジェクト.メソッド(...)` … 動作を命じる（例：`img.copy()`、`picam2.start()`）

---

## 2. 基本の形

```python
# 文字列もオブジェクト。メソッドを持っている
name = "leaf monitor"
print(name.upper())      # メソッド：大文字に → LEAF MONITOR
print(len(name))         # 長さ

# リストもオブジェクト
nums = [3, 1, 2]
nums.append(4)           # メソッド：末尾に追加
nums.sort()              # メソッド：並べ替え
print(nums)              # [1, 2, 3, 4]
```

`name` や `nums` のような身近な値も、実はオブジェクトで、たくさんのメソッドを持っています。

---

## 3. サンプルスクリプト

「属性」と「メソッド」のイメージをはっきりさせるため、小さなオブジェクト（クラス）を自分で作ってみましょう。`leaf_monitor.py` 自身はクラスを定義しませんが、概念をつかむには自作が一番です。

```python
# sample_object.py

class Pot:                       # 「鉢」というオブジェクトの設計図（クラス）
    def __init__(self, color):
        self.color = color       # 属性：色（持っているデータ）
        self.leaves = 0          # 属性：積もった落ち葉の数

    def add_leaf(self):          # メソッド：落ち葉を1枚足す動作
        self.leaves += 1

    def report(self):            # メソッド：状態を報告する動作
        print(f"{self.color}の鉢：落ち葉 {self.leaves} 枚")

# オブジェクト（実体）を作る ＝ インスタンス化
pot = Pot("青")

# 属性を見る
print("色は:", pot.color)

# メソッドで動作させる
pot.add_leaf()
pot.add_leaf()
pot.report()                     # 青の鉢：落ち葉 2 枚
```

実行結果：

```
色は: 青
青の鉢：落ち葉 2 枚
```

`pot` というオブジェクトが、`color`・`leaves` という**属性**（データ）と、`add_leaf()`・`report()` という**メソッド**（動作）を持っているのが分かります。これがオブジェクトの正体です。

---

## 4. 代表的な使い方

`leaf_monitor.py` は自分でクラスを定義しませんが、**ライブラリが用意したオブジェクトを使う**という、いちばん多いパターンを使っています。

- **インスタンス化**：クラスから実体を作る（`Picamera2()`、`argparse.ArgumentParser()`）。
- **メソッド呼び出し**：実体に動作を命じる（`picam2.start()`、`parser.add_argument(...)`）。
- **属性アクセス**：実体が持つデータを取り出す（`args.loop`、`img.shape`）。

> **やってみよう**
> `sample_object.py` の `Pot` に、`remove_leaf()`（落ち葉を1枚減らす）メソッドを足してみましょう。`self.leaves -= 1` を使います。オブジェクトに新しい動作を追加する感覚がつかめます。

---

## 5. leaf_monitor.py での実例

**(1) カメラオブジェクト** — `capture_image()`

```python
picam2 = Picamera2()                  # インスタンス化（実体を作る）
config = picam2.create_still_configuration(main={"size": RESOLUTION})  # メソッド
picam2.configure(config)              # メソッド
picam2.start()                        # メソッド
picam2.capture_file(path)             # メソッド
picam2.stop()                         # メソッド
picam2.close()                        # メソッド
```

`Picamera2()` でカメラの実体を作り、`.start()` や `.capture_file()` といったメソッドで「もの」に動作を命じています。`sample_object.py` の `pot.add_leaf()` と同じ構図です。

**(2) 画像オブジェクト（NumPy 配列）** — あちこち

```python
print(img.shape)          # 属性：画像の形
annotated = img.copy()    # メソッド：複製を作る
```

画像（NumPy 配列）もオブジェクトで、`.shape` という**属性**や `.copy()` という**メソッド**を持っています。

**(3) 引数オブジェクト** — `main()`

```python
args = parser.parse_args()
if args.calibrate:        # 属性アクセス
    ...
```

`parse_args()` が返すオブジェクト `args` から、`args.calibrate`・`args.loop` という属性を取り出しています。

---

## 6. まとめ

- オブジェクトは「**データ（属性）＋動作（メソッド）**」をひとまとめにしたもの。
- `オブジェクト.属性` でデータを取り出し、`オブジェクト.メソッド(...)` で動作を命じる。
- クラスから実体を作ることを**インスタンス化**という（`Picamera2()` など）。
- Python ではほぼすべてがオブジェクト（文字列・リスト・NumPy 配列も）。
- `leaf_monitor.py` は、ライブラリのオブジェクト（カメラ・引数・画像）を使う形でオブジェクトを活用している。
