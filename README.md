# raspi5-opencv-leaf-monitor

Raspberry Pi 5 と OpenCV で、鉢の周りに積もった落ち葉（堆積物）が色付きマットの何パーセントを覆っているか（**被覆面積率**）を自動計測する `leaf_monitor.py` と、それを題材にした **OpenCV / NumPy 入門教材** の一式です。

被覆面積率を時系列で記録することで、ミニトマトの落葉傾向＝健康状態のトレンドを見守ることを目的としています。教材は、高校情報レベルの Python 知識を出発点に、最終的に `leaf_monitor.py` の中身をすべて自分の言葉で説明できるようになることを目指して書かれています。

## 対象読者と前提環境

- **対象**：高校情報レベル（条件分岐・くりかえし・関数）の Python 経験者。画像処理は初めてでも大丈夫です。
- **ハードウェア**：Raspberry Pi 5 ＋ Camera Module v1.3（OV5647）
- **OS / 開発**：Raspberry Pi OS Lite（Bookworm）、Windows 11 の VS Code から Remote-SSH で Pi 上を編集・実行
- 画面のない環境を前提に、確認は「画像をファイル保存 → VS Code で開く」で行います。

## リポジトリ構成

```
.
├── textbook/        教材（マークダウン）
│   ├── README.md        教材の目次（ここから読み始める）
│   ├── textbook.md      本編の通し読み版（第0〜10章）
│   ├── chapters/        章ごとの個別ファイル（00〜10）
│   ├── appendix/        付録A・C・D・E
│   └── glossary/        用語解説 B01〜B09
├── src/             実行コード
│   ├── leaf_monitor.py            本体（動かす用）
│   └── leaf_monitor_annotated.py  注釈版（教材と対応した学習用）
└── samples/
    └── step_scripts/   第1〜8章のハンズオン step1.py〜step23.py（＋README）
```

## 教材の読み方

1. [教材の目次（textbook/README.md）](textbook/README.md) を開く
2. [本編（textbook/textbook.md）](textbook/textbook.md) を第0章から順に読む
3. 文法でつまずいたら `textbook/glossary/`、さらに深めたいときは `textbook/appendix/` を参照
4. ハンズオンは `samples/step_scripts/` のスクリプトを実機で動かす
5. 最後に `src/leaf_monitor_annotated.py` を読み、学んだ道具を回収する

## セットアップ（Raspberry Pi 5 / Raspberry Pi OS Lite）

```bash
# システム更新
sudo apt update && sudo apt full-upgrade -y

# カメラ動作確認（エラーが出なければ認識OK）
rpicam-hello --timeout 2000

# 必要ライブラリ（システムPythonに導入するのが最も簡単）
sudo apt install -y python3-picamera2 --no-install-recommends
sudo apt install -y python3-opencv python3-numpy
```

## 使い方

```bash
# 0) 学習用のハンズオン作業フォルダ（任意）
#    教材のサンプルは ~/opencv_lesson での実行を想定しています。

# 1) キャリブレーション（掃除直後・鉢あり・堆積物なしで実行）
python3 src/leaf_monitor.py --calibrate

# 2) 単発計測
python3 src/leaf_monitor.py

# 3) ループ実行（例：1時間ごと）
python3 src/leaf_monitor.py --loop 3600
```

`--calibrate` で `mat_config.json` / `region.png` / `pot.png` が作られ、計測のたびに `log.csv` と `annotated/<日時>.jpg`（青＝計測範囲・黄＝鉢・緑＝堆積物）が出力されます。詳細は教材第9・10章を参照してください。

## ライセンス

- **ソースコード**（`src/`、`samples/`）：MIT License
- **教材**（`textbook/`）：Creative Commons Attribution 4.0 International（CC BY 4.0）

詳細は [LICENSE](LICENSE) を参照してください。

## 注意

実行すると `captures/` `annotated/` などの画像や `log.csv` などが生成されます。これらは `.gitignore` で除外しています。公開前に、設置場所のパスや IP などの個人情報が含まれていないか確認してください。
