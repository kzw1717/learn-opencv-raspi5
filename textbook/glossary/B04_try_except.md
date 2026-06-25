# 用語解説：try-except（例外処理）

> `leaf_monitor.py` には、カメラ用ライブラリの読み込みを `try` で囲んだり、無限ループを `try` で囲んで Ctrl+C で止めたりする箇所があります。
> この `try`-`except` は「**エラーが起きても、プログラムを止めずに対処する**」ための仕組みです。

---

## 1. これは何？（考え方）

プログラムは、エラーが起きると**そこで止まって**しまいます。たとえば「無いファイルを開こうとした」「0で割った」「ライブラリが入っていなかった」など。

でも、エラーが起きたときに「止まる」のではなく「**こう対処する**」と決めておきたいことがあります。`try`-`except` はそのための書き方です。

> 「**`try` の中でエラーが起きたら、`except` の中の処理に切り替える**」

「とりあえずやってみて（try）、ダメだったらこうする（except）」という保険だと思ってください。

---

## 2. 基本の形

```python
try:
    # エラーが起きるかもしれない処理
    ...
except エラーの種類:
    # エラーが起きたときの対処
    ...
```

`except` のうしろに「エラーの種類」を書くと、その種類のエラーだけを捕まえます。代表的な種類：

| エラーの種類 | いつ起きるか |
|---|---|
| `ZeroDivisionError` | 0で割ったとき |
| `FileNotFoundError` | 無いファイルを開こうとしたとき |
| `ImportError` | ライブラリの読み込みに失敗したとき |
| `KeyboardInterrupt` | Ctrl+C で止めたとき |

---

## 3. サンプルスクリプト

エラーで止まる場合と、`try`-`except` で対処する場合を比べてみましょう。

```python
# sample_try.py

# ── 対処しないと、ここで止まってしまう ──
# print(10 / 0)   # ← コメントを外すと ZeroDivisionError で停止

# ── try-except で対処する ──
def safe_coverage(leaf_area, region_area):
    try:
        return 100.0 * leaf_area / region_area
    except ZeroDivisionError:
        print("計測範囲が0です。0%として扱います。")
        return 0.0

print(safe_coverage(300, 1500))   # 20.0
print(safe_coverage(300, 0))      # 0で割りそうになるが、止まらず 0.0

# ── 無いファイルを開こうとしたとき ──
try:
    with open("ない.txt") as f:
        print(f.read())
except FileNotFoundError:
    print("ファイルが見つかりませんでした。")
```

実行結果：

```
20.0
計測範囲が0です。0%として扱います。
0.0
ファイルが見つかりませんでした。
```

`safe_coverage(300, 0)` は本来 0 で割ってエラーになりますが、`except` のおかげで止まらず、代わりに 0.0 を返しています。

> 補足：`leaf_monitor.py` の被覆率計算は、`try` ではなく `if region_area else 0.0`（条件式）で 0 割りを防いでいます。どちらも「0 割りで止めない」工夫です。場面に応じて使い分けます。

---

## 4. 代表的な使い方

- **無いかもしれないものを扱う**：ファイル・ライブラリ・ネット接続など、失敗しうる処理の保険。
- **ユーザーの中断を受け止める**：Ctrl+C（`KeyboardInterrupt`）をきれいに処理して終了する。
- **分かりやすいエラーメッセージに変える**：謎のエラーで落ちる代わりに、対処法を表示して終わる。

> **やってみよう**
> `sample_try.py` の `except FileNotFoundError:` を消して、無いファイルを開いてみましょう。プログラムがエラーで止まることが分かります。`try`-`except` の「止めない」ありがたみが実感できます。

---

## 5. leaf_monitor.py での実例

**(1) ライブラリが無くても親切に終わる** — `capture_image()`

```python
try:
    from picamera2 import Picamera2
except ImportError:
    sys.exit("picamera2 が見つかりません。"
             "`sudo apt install -y python3-picamera2 ...` を実行してください。")
```

カメラ用ライブラリ picamera2 の読み込みを `try` で囲み、失敗（`ImportError`）したら、謎のエラーで落ちる代わりに**インストール方法を表示して終了**します。初心者にやさしい設計です。

**(2) Ctrl+C でループをきれいに止める** — `main()`

```python
try:
    while True:
        run_once()
        time.sleep(args.loop)
except KeyboardInterrupt:
    print("\n停止しました。")
```

`--loop` の無限ループ（`while True:`）を `try` で囲み、Ctrl+C（`KeyboardInterrupt`）が押されたら、エラー表示ではなく「停止しました。」と表示して、きれいに終わります。

---

## 6. まとめ

- `try`-`except` は「エラーが起きても止めずに対処する」仕組み。
- 形は `try:`（やってみる）→ `except エラーの種類:`（ダメだったときの対処）。
- 代表的なエラー：`ZeroDivisionError`・`FileNotFoundError`・`ImportError`・`KeyboardInterrupt`。
- `leaf_monitor.py` では「ライブラリ不足を親切に知らせる」「Ctrl+C できれいに止める」のに使われている。
