# 用語解説：import文

> `leaf_monitor.py` は、`import cv2` や `import numpy as np`、`from datetime import datetime` など、たくさんの `import` で始まっています。
> `import` は「**他の人が作った便利な道具（ライブラリ）を借りてくる**」ための文です。

---

## 1. これは何？（考え方）

Python には、世界中の人が作った便利な機能の集まり（**ライブラリ／モジュール**）があります。画像処理なら OpenCV、数値計算なら NumPy、日時なら datetime…という具合です。

これらを自分のプログラムで使うには、まず「借りてくる」必要があります。それが `import` 文です。

> `import` は「このライブラリの機能を、これから使います」という宣言。

毎回ゼロから自分で書く必要はなく、`import` 一行で巨大な機能を呼び出せます。プログラムがファイルの先頭で `import` をずらりと並べるのは、「この料理に使う材料（道具）はこれです」と最初に宣言しているようなものです。

---

## 2. 基本の形（3種類）

```python
# (A) まるごと借りて、「ライブラリ名.機能」で使う
import cv2
img = cv2.imread("a.jpg")

# (B) 別名（短い名前）を付けて借りる
import numpy as np
arr = np.array([1, 2, 3])

# (C) 中の特定の機能だけ名指しで借りる
from datetime import datetime
now = datetime.now()
```

| 書き方 | 使うとき | 例 |
|---|---|---|
| `import X` | ライブラリ全体を借りる | `import cv2` → `cv2.imread(...)` |
| `import X as Y` | 長い名前を短い別名にする | `import numpy as np` → `np.array(...)` |
| `from X import Y` | 中の一部だけ借りる | `from datetime import datetime` → `datetime.now()` |

`as np` のような別名は、慣習として決まっているものもあります（NumPy はみんな `np`）。

---

## 3. サンプルスクリプト

3種類の `import` を実際に使ってみましょう。

```python
# sample_import.py

# (A) 標準ライブラリ math をまるごと借りる
import math
print("円周率:", math.pi)
print("16の平方根:", math.sqrt(16))

# (B) 別名を付けて借りる
import numpy as np
arr = np.array([10, 20, 30])
print("配列の合計:", arr.sum())

# (C) 中の一部だけ名指しで借りる
from datetime import datetime
print("いまの時刻:", datetime.now().strftime("%H:%M:%S"))
```

実行結果（一部）：

```
円周率: 3.141592653589793
16の平方根: 4.0
配列の合計: 60
いまの時刻: 14:35:02
```

`math.pi`（A）、`np.array`（B）、`datetime.now`（C）と、借り方によって呼び出し方が変わる点に注目してください。

---

## 4. 代表的な使い方

- **標準ライブラリを使う**：`os`・`sys`・`json`・`csv`・`time`・`datetime` など、最初から付いてくる道具。インストール不要。
- **外部ライブラリを使う**：`cv2`（OpenCV）・`numpy` など、`apt` や `pip` で別途入れた道具。
- **別名でタイプを減らす**：`import numpy as np` のように、よく使う長い名前を短くする。

> **注意：インストール名と import 名は違うことがある**
> 画像処理ライブラリは、インストールは `python3-opencv` なのに、`import cv2` で読み込みます。「OpenCV ＝ cv2」とセットで覚えておきましょう。

---

## 5. leaf_monitor.py での実例

`leaf_monitor.py` の先頭には、3種類すべての `import` が並んでいます。

```python
import argparse        # (A) 標準ライブラリをまるごと
import csv
import json
import os
import sys
import time
from datetime import datetime   # (C) datetime の中の datetime だけ

import cv2              # (A) 外部ライブラリ OpenCV
import numpy as np      # (B) 外部ライブラリ NumPy に別名 np
```

さらに、関数の中で必要になったときに import している箇所もあります。

```python
# capture_image() の中
try:
    from picamera2 import Picamera2   # (C) picamera2 の中の Picamera2 だけ
except ImportError:
    sys.exit("picamera2 が見つかりません。...")
```

カメラ用ライブラリは無い環境もあるため、あえて関数の中で `try` と一緒に import し、無ければ親切に知らせる作りになっています（→ try-except の解説も参照）。

---

## 6. まとめ

- `import` は「他の人が作った便利な道具（ライブラリ）を借りてくる」文。
- 3種類：`import X`（まるごと）／`import X as Y`（別名）／`from X import Y`（一部だけ）。
- 標準ライブラリ（os・json・csv・datetime…）はインストール不要、外部ライブラリ（cv2・numpy…）は別途インストールが必要。
- インストール名と import 名が違うことがある（python3-opencv → `import cv2`）。
- `leaf_monitor.py` は3種類すべての import を使っている。
