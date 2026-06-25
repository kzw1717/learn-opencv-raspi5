# 用語解説：辞書型（dict）

> `leaf_monitor.py` は、学習したマットの色を `{"lower": ..., "upper": ..., "peak_hue": ...}` という形でファイルに保存し、あとで `cfg["lower"]` のように取り出します。
> この `{ }` と「名前で取り出す」仕組みが**辞書型（dict）**です。リストと並ぶ、基本の入れものです。

---

## 1. これは何？（考え方）

辞書型は、ひとことで言うと

> 「**名前（キー）→値**」の対応表

です。本物の辞書が「単語→意味」で引けるように、Python の辞書は「キー→値」で引けます。

リストは「0番目・1番目…」と**番号**で取り出しました。辞書は番号ではなく「`lower`」「`upper`」といった**名前**で取り出せるのが違いです。`lower[0]` より `cfg["lower"]` のほうが、何を取り出しているか一目で分かりますね。

---

## 2. 基本の形

```python
# 作る：{ キー: 値, キー: 値, ... }
config = {"lower": [108, 100, 110], "upper": [132, 240, 255]}

# 取り出す：辞書[キー]
print(config["lower"])        # [108, 100, 110]

# 追加・変更：辞書[キー] = 値
config["peak_hue"] = 120

# キーがあるか調べる
print("lower" in config)      # True

# 安全に取り出す（無ければ初期値）
print(config.get("memo", "なし"))   # なし
```

キーには文字列（`"lower"` など）がよく使われます。値には数値・文字列・リストなど、何でも入れられます。

---

## 3. サンプルスクリプト

`leaf_monitor.py` の「マット色設定を辞書にして JSON ファイルに保存し、読み戻す」流れを、小さく再現してみましょう。

```python
# sample_dict.py
import json

# マット色の設定を辞書で表す
mat_config = {
    "lower": [108, 100, 110],
    "upper": [132, 240, 255],
    "peak_hue": 120,
}

# 名前（キー）で取り出す
print("色相の中心:", mat_config["peak_hue"])
print("下限:", mat_config["lower"])

# 辞書 → JSON ファイルに保存
with open("mat_config.json", "w") as f:
    json.dump(mat_config, f, indent=2)
print("mat_config.json に保存しました。")

# JSON ファイル → 辞書に読み戻す
with open("mat_config.json") as f:
    loaded = json.load(f)
print("読み戻した上限:", loaded["upper"])
```

実行結果（一部）：

```
色相の中心: 120
下限: [108, 100, 110]
mat_config.json に保存しました。
読み戻した上限: [132, 240, 255]
```

保存された `mat_config.json` を VS Code で開くと、辞書がそのままの形でテキストになっているのが分かります。**辞書と JSON は形がそっくり**なので、設定の保存にぴったりなのです。

---

## 4. 代表的な使い方

- **設定やひとまとまりの情報を名前付きで持つ**：`{"lower": ..., "upper": ...}` のように。
- **JSON ファイルとの往復**：`json.dump(辞書, f)` で保存、`json.load(f)` で読み込み。設定ファイルの定番。
- **キーで素早く引く**：番号を覚えなくても、意味のある名前で取り出せる。

> **やってみよう**
> `sample_dict.py` の `mat_config` に `"memo": "青いマット"` のような項目を足して保存し直し、読み戻して表示してみましょう。辞書は後から項目を増やせます。

---

## 5. leaf_monitor.py での実例

**(1) 辞書を作って JSON 保存** — `calibrate()`

```python
with open(MAT_CONFIG, "w") as f:
    json.dump({"lower": lower, "upper": upper, "peak_hue": peak}, f, indent=2)
```

学習した下限・上限・代表色相を、その場で辞書にして保存しています。`sample_dict.py` と同じやり方です。

**(2) JSON を読み戻してキーで取り出す** — `load_mat_config()`

```python
with open(MAT_CONFIG) as f:
    cfg = json.load(f)
return np.array(cfg["lower"]), np.array(cfg["upper"])
```

読み込んだ辞書 `cfg` から、`cfg["lower"]`・`cfg["upper"]` と**名前で**取り出しています。番号ではなく名前で引けるので、コードが読みやすくなっています。

---

## 6. まとめ

- 辞書型は「**キー（名前）→値**」の対応表。`{ }` で作る。
- 取り出しは `辞書[キー]`。番号ではなく意味のある名前で引ける。
- 後から項目を追加・変更できる。`in` で存在確認、`.get()` で安全に取得。
- 辞書は JSON とそっくりなので、`json.dump`／`json.load` で設定の保存・読込に使われる。
- `leaf_monitor.py` はマット色設定を辞書＋JSON で保存・読み戻している。
