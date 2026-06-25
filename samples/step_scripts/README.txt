OpenCV入門テキスト 付録C 全stepスクリプト集
=============================================

これは「raspi5-opencv入門テキスト」第1〜8章のハンズオンで作る
step1.py〜step23.py を、ファイル単位でまとめたものです。

■ 実行環境
  - Raspberry Pi 5 + Camera Module v1.3 上で、VS Code の Remote-SSH 経由で実行
  - 作業フォルダ: ~/opencv_lesson
  - 実行: python3 stepN.py
  - 画面のない Pi では結果をウィンドウ表示できないため、
    保存された画像は VS Code のファイル一覧でクリックして確認する

■ 事前の撮影（最初に2枚撮っておく）
  cd ~/opencv_lesson
  rpicam-jpeg -o sample.jpg --timeout 2000   # 第1章用
  rpicam-jpeg -o mat.jpg    --timeout 2000   # 第2章以降用（マット＋落ち葉）
  # step7.py 用に、明るさ違いの2枚も撮っておく
  rpicam-jpeg -o mat_bright.jpg --timeout 2000
  rpicam-jpeg -o mat_dark.jpg   --timeout 2000

■ 成果物の流れ
  sample.jpg（第1章）
  mat.jpg（第2章：撮影）
    → mat_mask.jpg（第3章：マット色マスク）
        → not_mat.jpg（第5章：反転）
        → leaf.jpg（第5章：範囲内のマット色でない部分＝堆積物）
    → mat_region.jpg（第6章：凸包で埋めたマット外形）
        → annotated_full.jpg（第8章：確認画像）

■ どの step で何を学ぶか
  step1-4   第1章 画像は数字の表（imread/imwrite/cvtColor GRAY）
  step5-7   第2章 HSV（cvtColor）
  step8-10  第3章 マスク（inRange）
  step11-13 第4章 モルフォロジー（morphologyEx/dilate）
  step14-15 第5章 ビット演算（bitwise_not/and）
  step16-19 第6章 輪郭・凸包（findContours/contourArea/convexHull/fillPoly）
  step20-21 第7章 面積・被覆率（countNonZero）
  step22-23 第8章 可視化（drawContours/putText）
