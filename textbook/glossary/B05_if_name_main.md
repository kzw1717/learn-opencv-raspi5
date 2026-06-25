# 用語解説：if __name__ == "__main__":

> `leaf_monitor.py` のいちばん最後には、おまじないのような `if __name__ == "__main__":` という行があります。
> これは「このファイルを**直接実行したときだけ** main() を動かす」という、Python の定番の書き方です。

---

## 1. これは何？（考え方）

Python のファイル（モジュール）には、2通りの使われ方があります。

1. **直接実行する**：`python3 leaf_monitor.py` のように、そのファイルを動かす。
2. **import される**：別のファイルから `import` されて、関数だけを借りられる。

このとき、「直接実行したときだけ動かしたい処理」があります。たとえば `leaf_monitor.py` の `main()`（撮影や計測の実行）は、**直接実行したときだけ**動いてほしい。もし別のファイルが「`analyze()` だけ借りたい」と import しただけで勝手にカメラが起動したら困りますよね。

そこで使うのが、`if __name__ == "__main__":` です。

> このファイルが**直接実行されたときだけ**、この中身を動かす。import されただけなら動かさない。

---

## 2. 基本の形（しくみ）

Python は、ファイルごとに `__name__` という特別な変数を自動でセットします。

- そのファイルを**直接実行**したとき → `__name__` は `"__main__"` になる。
- そのファイルが**import**されたとき → `__name__` はファイル名（モジュール名）になる。

だから次のように書くと、「直接実行のときだけ」を判定できます。

```python
def main():
    print("メインの処理")

if __name__ == "__main__":   # 直接実行されたときだけ True
    main()
```

---

## 3. サンプルスクリプト

2つのファイルを作って、動きの違いを確かめましょう。

**ファイル1：`mymodule.py`（部品）**

```python
# mymodule.py

def greet():
    print("greet() が呼ばれました")

print("このファイルの __name__ は:", __name__)

if __name__ == "__main__":
    print("→ 直接実行されたので main 部分を動かします")
    greet()
```

**ファイル2：`use_module.py`（mymodule を借りる側）**

```python
# use_module.py
import mymodule          # ここで mymodule.py が読み込まれる

print("--- import 完了 ---")
mymodule.greet()          # 関数だけ借りて使う
```

**それぞれ実行してみる：**

```bash
python3 mymodule.py
```
```
このファイルの __name__ は: __main__
→ 直接実行されたので main 部分を動かします
greet() が呼ばれました
```

```bash
python3 use_module.py
```
```
このファイルの __name__ は: mymodule
--- import 完了 ---
greet() が呼ばれました
```

ポイントは、`use_module.py` を実行したとき（＝`mymodule` を import したとき）、`mymodule.py` の `if __name__ == "__main__":` の中が**動いていない**ことです。`__name__` が `"mymodule"` になっているからです。一方で、`greet()` という関数はちゃんと借りて使えています。

---

## 4. 代表的な使い方

- **「実行ファイル」と「部品」を両立させる**：直接実行すれば動くアプリにもなり、import すれば関数を貸せる部品にもなる。
- **テストや動作確認の入り口**：「このファイル単体で動かしたときだけ、お試し処理を動かす」のに使う。

> **やってみよう**
> `mymodule.py` の `if __name__ == "__main__":` の行を消して（中身はインデントを戻して残す）、`use_module.py` を実行してみましょう。import しただけなのに main 部分が動いてしまい、なぜこの仕組みが必要かが分かります。

---

## 5. leaf_monitor.py での実例

`leaf_monitor.py` の末尾はこうなっています。

```python
def main():
    parser = argparse.ArgumentParser(...)
    ...
    # --calibrate / --loop / 引数なし で処理を振り分ける

if __name__ == "__main__":
    main()
```

`python3 leaf_monitor.py --calibrate` のように**直接実行**したときだけ `main()` が動き、コマンドライン引数に応じてキャリブレーションや計測を行います。

もし将来、別のスクリプトから「`leaf_monitor.py` の `analyze()` だけ借りたい」となっても、`import leaf_monitor` したときに `main()`（＝カメラ起動など）が勝手に動く心配はありません。この1行が、その安全を守っています。

---

## 6. まとめ

- `if __name__ == "__main__":` は「このファイルを**直接実行したときだけ**動かす」ための定番の書き方。
- `__name__` は、直接実行なら `"__main__"`、import されたらモジュール名になる特別な変数。
- これにより、1つのファイルが「実行アプリ」と「部品（import される側）」を両立できる。
- `leaf_monitor.py` では、直接実行のときだけ `main()` を呼ぶために使われている。
