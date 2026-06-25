# もくじ ── OpenCV 入門テキスト（leaf_monitor.py を読むために）

> このテキストは、Raspberry Pi 5 で動く落ち葉モニタリング・プログラム `leaf_monitor.py` を題材に、OpenCV の使い方を一段ずつ学ぶ入門教材です。
> 高校情報レベルの Python 知識を出発点に、最終的に `leaf_monitor.py` の OpenCV をすべて自分の言葉で説明できるようになることを目指します。

---

## このテキストの前提

- 本体：Raspberry Pi 5（カメラ：Camera Module v1.3 / OV5647）、OS：Raspberry Pi OS Lite
- 開発：Windows 11 の VS Code から Remote-SSH で Pi に接続し、Pi 上で編集・実行
- 画面のない環境なので、確認は「`cv2.imwrite` で保存 → VS Code で開く」で行う
- 作業フォルダ：`~/opencv_lesson/`

---

## 本編（第0章〜第10章）

各章は「ゴール → 動機 → ハンズオン（step スクリプト＋やってみよう）→ `leaf_monitor.py` への橋渡し → まとめ → 確認問題」で構成しています。

| 章 | タイトル | 主に学ぶ OpenCV | ファイル |
|---|---|---|---|
| 第0章 | ゴールの先取りと準備 | （全体像・環境確認） | [00_ゴールと準備.md](chapters/00_goal_and_setup.md) |
| 第1章 | 画像は数字の表 | `imread`・`imwrite`・`cvtColor`(GRAY) | [01_画像は数字の表.md](chapters/01_image_as_array.md) |
| 第2章 | 色を分けて考える（HSV） | `cvtColor`(HSV) | [02_色を分けて考えるHSV.md](chapters/02_hsv.md) |
| 第3章 | マスクを作る | `inRange` | [03_マスクを作る.md](chapters/03_mask.md) |
| 第4章 | マスクの掃除（モルフォロジー） | `getStructuringElement`・`morphologyEx`・`dilate` | [04_マスクの掃除モルフォロジー.md](chapters/04_morphology.md) |
| 第5章 | マスクを組み合わせる（ビット演算） | `bitwise_not`・`bitwise_and` | [05_マスクを組み合わせるビット演算.md](chapters/05_bitwise.md) |
| 第6章 | 形を見つける（輪郭・凸包） | `findContours`・`contourArea`・`convexHull`・`fillPoly` | [06_形を見つける輪郭と凸包.md](chapters/06_contours.md) |
| 第7章 | 面積を測る（被覆面積率） | `countNonZero` | [07_面積を測る被覆面積率.md](chapters/07_coverage.md) |
| 第8章 | 結果を描く（可視化） | `drawContours`・`putText` | [08_結果を描く可視化.md](chapters/08_visualize.md) |
| 第9章 | leaf_monitor.py を通して読む | （総まとめ・全関数の回収） | [09_leaf_monitorを通して読む.md](chapters/09_read_leaf_monitor.md) |
| 第10章 | 実際に運用する（発展） | （キャリブレーション・cron・チューニング） | [10_実際に運用する.md](chapters/10_operation.md) |

---

## 付録・解説

| 種別 | タイトル | 内容 | ファイル |
|---|---|---|---|
| 付録A | Python の構文・型・ライブラリ一覧 | OpenCV 以外の Python 要素の早見表 | [A_Python構文と型とライブラリ.md](appendix/A_python_basics.md) |
| 付録C | 全 step スクリプト集 | 第1〜8章の step1〜step23 をまとめて掲載 | [C_全stepスクリプト集.md](appendix/C_step_scripts.md) |
| 付録D | 確認問題の解答集 | 第1〜9章の確認問題の模範解答例 | [D_確認問題の解答集.md](appendix/D_answers.md) |
| 付録E | OpenCV のための NumPy 入門 | カメラ撮影画像を NumPy で処理しながら学ぶ。配列・オブジェクト・ファイルオブジェクトも解説 | [E_OpenCVのためのNumpy入門.md](appendix/E_numpy_for_opencv.md) |

### 用語解説（高校生がつまずきやすい要素）

`leaf_monitor.py` に出てくる、少し難しい Python 要素の個別解説です。必要になった章で参照してください。

| 用語 | よく出てくる章 | ファイル |
|---|---|---|
| リスト内包表記 | 第6章 | [B01_リスト内包表記.md](glossary/B01_list_comprehension.md) |
| 辞書型（dict） | 第9章 | [B02_辞書型.md](glossary/B02_dict.md) |
| with | 第9章（CSV/JSON） | [B03_with.md](glossary/B03_with.md) |
| try-except | 第9章・第10章 | [B04_try-except.md](glossary/B04_try_except.md) |
| if __name__ == "__main__": | 第9章 | [B05_if_name_main.md](glossary/B05_if_name_main.md) |
| import文 | 全章 | [B06_import文.md](glossary/B06_import.md) |
| オブジェクト | 全章 | [B07_オブジェクト.md](glossary/B07_object.md) |
| ファイルオブジェクト | 第9章 | [B08_ファイルオブジェクト.md](glossary/B08_file_object.md) |
| NumPy | 第1章〜全章 | [B09_NumPy.md](glossary/B09_numpy.md) |

---

## おすすめの読み進め方

基本は **第0章から順番に**進めるのがいちばんです。各章のハンズオンを実際に Pi で動かし、保存された画像を VS Code で見ながら読むと、理解が一気に深まります。

Python の文法でつまずいたら、本編を止めて該当する **用語解説（B01〜B09）** を読み、戻ってくるとスムーズです。たとえば第6章でリスト内包表記が出てきて戸惑ったら B01 を、第9章で `with` や辞書が気になったら B03・B02 を参照してください。

各章末の **確認問題** を解いたら、**付録D** で答え合わせをしましょう。手を動かした step スクリプトを後から見返したいときは、**付録C** にすべてまとまっています。NumPy の使われ方をもう少し深く、撮影画像を使って手を動かしながら理解したくなったら、**付録E** がカメラ撮影から `leaf_monitor.py` の NumPy 読解までを橋渡しします（配列・オブジェクト・ファイルオブジェクトの解説も含みます）。

第9章まで終えれば、最初は難しく見えた `leaf_monitor.py` が「学んだ道具の組み合わせ」として読めるようになっているはずです。
