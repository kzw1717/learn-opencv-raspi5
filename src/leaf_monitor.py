#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
leaf_monitor.py
ミニトマトの落ち葉モニタリング (Raspberry Pi 5 + Camera Module v1.3 / OV5647)

用途: 鉢周辺の落ち葉の「増加トレンド」を被覆面積率で監視
手法: 色付きマットのHSV色抽出。鉢などの固定物は除外し、計測範囲は
      キャリブレーション時に固定 → 分母が一定なので日々の比較が正しくできる。
指標: 被覆面積率(%) = 落ち葉面積 / 固定有効マット面積 × 100

使い方:
  1) 鉢・支柱は通常どおり置き、落ち葉だけ無い状態でキャリブレーション
     （最初に1回 + マット/鉢/照明/カメラ位置を変えたら都度）
       python3 leaf_monitor.py --calibrate
  2) 計測（cronやループで定期実行）
       python3 leaf_monitor.py
  3) cronを使わずループ実行（例: 1時間ごと）
       python3 leaf_monitor.py --loop 3600

出力:
  - mat_config.json   : 学習したマット色のHSV範囲
  - region.png        : 固定された計測範囲（鉢を除いた有効マット）
  - pot.png           : 鉢など除外領域（確認表示用）
  - log.csv           : 日時, 被覆面積率(%), 落ち葉の塊数
  - captures/*.jpg     : 撮影した生画像
  - annotated/*.jpg    : 検出結果を重ねた確認用画像
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime

import cv2
import numpy as np

# ===================== 設定（環境に合わせて調整） =====================
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
MAT_CONFIG    = os.path.join(BASE_DIR, "mat_config.json")
REGION_MASK   = os.path.join(BASE_DIR, "region.png")   # 固定の計測範囲
POT_MASK      = os.path.join(BASE_DIR, "pot.png")       # 除外領域(表示用)
CAPTURE_DIR   = os.path.join(BASE_DIR, "captures")
ANNOTATED_DIR = os.path.join(BASE_DIR, "annotated")
LOG_CSV       = os.path.join(BASE_DIR, "log.csv")

RESOLUTION = (2028, 1520)   # OV5647フル解像度は2592x1944
SETTLE_SEC = 2.0

# --- マット色を見分けるHSV許容マージン ---
H_MARGIN = 12      # 色相 ±（OpenCVのHは0-180）。マット判定の主役なので狭め
S_MARGIN = 70      # 彩度 ±。照明変化に追従できるよう広め
V_MARGIN = 80      # 明度 ±。影でも拾えるよう広め

# --- キャリブレーション時に「色付きのマット画素」とみなす条件 ---
SAT_MIN = 50
VAL_MIN = 40
VAL_MAX = 245

# --- 領域・検出パラメータ ---
MORPH_KERNEL     = 5
MIN_MAT_FRAGMENT = 2000   # マット輪郭としてこれ以上の断片のみ採用（px）
MIN_LEAF_AREA    = 600    # これ未満は影・ノイズとして塊数から除外（px）
POT_DILATE       = 9      # 鉢マスクを少し太らせて縁の取りこぼしを防ぐ

# --- 鉢周辺に絞る設定 ---
# 0なら鉢を除いたマット全体を計測。正の値にすると鉢の縁からそのピクセル距離内
# （鉢を取り巻く帯状の範囲）だけを計測範囲にする。
FOCUS_BAND_PX = 0
# =====================================================================


def capture_image(path):
    """picamera2で1枚撮影してJPEG保存（色順の罠を避けるためファイル経由）。"""
    try:
        from picamera2 import Picamera2
    except ImportError:
        sys.exit("picamera2 が見つかりません。"
                 "`sudo apt install -y python3-picamera2 --no-install-recommends` を実行してください。")

    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": RESOLUTION})
    picam2.configure(config)
    picam2.start()
    time.sleep(SETTLE_SEC)
    picam2.capture_file(path)
    picam2.stop()
    picam2.close()
    return path


def load_mat_config():
    if not os.path.exists(MAT_CONFIG):
        sys.exit("マット色が未設定です。まず `--calibrate` を実行してください。")
    with open(MAT_CONFIG) as f:
        cfg = json.load(f)
    return np.array(cfg["lower"]), np.array(cfg["upper"])


def get_mat_mask(hsv, lower, upper):
    """マット色のマスク。色相が0/180をまたぐ場合（赤系）にも対応。"""
    if lower[0] < 0:
        lo1 = np.array([0, lower[1], lower[2]]);             up1 = np.array([upper[0], upper[1], upper[2]])
        lo2 = np.array([180 + lower[0], lower[1], lower[2]]); up2 = np.array([180, upper[1], upper[2]])
        return cv2.inRange(hsv, lo1, up1) | cv2.inRange(hsv, lo2, up2)
    if upper[0] > 180:
        lo1 = np.array([lower[0], lower[1], lower[2]]);      up1 = np.array([180, upper[1], upper[2]])
        lo2 = np.array([0, lower[1], lower[2]]);             up2 = np.array([upper[0] - 180, upper[1], upper[2]])
        return cv2.inRange(hsv, lo1, up1) | cv2.inRange(hsv, lo2, up2)
    return cv2.inRange(hsv, lower.astype(np.uint8), upper.astype(np.uint8))


def mat_region_from_mask(mat_color):
    """マット色マスクからマットの外形（断片をまとめた凸包）を塗りつぶして返す。"""
    cnts, _ = cv2.findContours(mat_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pts = [c for c in cnts if cv2.contourArea(c) >= MIN_MAT_FRAGMENT]
    if not pts:
        if not cnts:
            return None
        pts = [max(cnts, key=cv2.contourArea)]
    hull = cv2.convexHull(np.vstack(pts))
    region = np.zeros(mat_color.shape, dtype=np.uint8)
    cv2.fillPoly(region, [hull], 255)
    return region


def analyze(img_bgr, lower, upper, region, pot):
    """固定計測範囲 region の中で、マット色でない部分＝落ち葉として被覆率を出す。"""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mat_color = get_mat_mask(hsv, lower, upper)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL, MORPH_KERNEL))
    mat_color = cv2.morphologyEx(mat_color, cv2.MORPH_OPEN, k, iterations=1)

    # 固定範囲内で「マット色でない」＝落ち葉
    leaf_mask = cv2.bitwise_and(region, cv2.bitwise_not(mat_color))
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, k, iterations=1)
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, k, iterations=2)

    region_area = int(cv2.countNonZero(region))   # ★ 固定なので毎回同じ
    leaf_area   = int(cv2.countNonZero(leaf_mask))
    coverage_pct = 100.0 * leaf_area / region_area if region_area else 0.0

    leaf_cnts, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    clumps = [c for c in leaf_cnts if cv2.contourArea(c) >= MIN_LEAF_AREA]

    annotated = img_bgr.copy()
    rcnts, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(annotated, rcnts, -1, (255, 0, 0), 2)   # 計測範囲: 青
    if pot is not None:
        pcnts, _ = cv2.findContours(pot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(annotated, pcnts, -1, (0, 255, 255), 2)  # 除外(鉢): 黄
    cv2.drawContours(annotated, clumps, -1, (0, 255, 0), 2)  # 落ち葉: 緑
    label = f"coverage={coverage_pct:.2f}%  clumps={len(clumps)}"
    cv2.putText(annotated, label, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    return coverage_pct, len(clumps), annotated


def append_log(timestamp, coverage, clumps):
    new_file = not os.path.exists(LOG_CSV)
    with open(LOG_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "coverage_pct", "clumps"])
        w.writerow([timestamp, f"{coverage:.3f}", clumps])


def calibrate():
    """鉢を置いたまま落ち葉無しの状態を撮影し、マット色学習＋固定計測範囲を作る。"""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    print("マット上に鉢・支柱は通常どおり置き、落ち葉が無い状態で撮影します...")
    path = os.path.join(CAPTURE_DIR, "_calib.jpg")
    capture_image(path)
    img = cv2.imread(path)
    if img is None:
        sys.exit("撮影画像の読み込みに失敗しました。")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    Hc, Sc, Vc = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # 有彩色画素の色相ヒストグラム最頻値＝マット色（鉢が中央でもマット最大面積なら拾える）
    valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)
    if np.count_nonzero(valid) < 1000:
        sys.exit("色付き画素が少なすぎます。マットがフレームに大きく写るようにしてください。")
    peak = int(np.argmax(np.bincount(Hc[valid].ravel(), minlength=180)))

    hue_dist = np.minimum(np.abs(Hc.astype(int) - peak), 180 - np.abs(Hc.astype(int) - peak))
    matpix = valid & (hue_dist <= H_MARGIN)
    s_med, v_med = int(np.median(Sc[matpix])), int(np.median(Vc[matpix]))

    lower = [peak - H_MARGIN, max(0, s_med - S_MARGIN), max(0, v_med - V_MARGIN)]
    upper = [peak + H_MARGIN, min(255, s_med + S_MARGIN), min(255, v_med + V_MARGIN)]
    with open(MAT_CONFIG, "w") as f:
        json.dump({"lower": lower, "upper": upper, "peak_hue": peak}, f, indent=2)

    mat_color = get_mat_mask(hsv, np.array(lower), np.array(upper))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL, MORPH_KERNEL))
    mat_color = cv2.morphologyEx(mat_color, cv2.MORPH_OPEN, k, iterations=1)
    mat_region = mat_region_from_mask(mat_color)
    if mat_region is None:
        sys.exit("マットが検出できませんでした。色や照明を確認してください。")

    # 鉢など固定物 = マット範囲内でマット色でない部分
    pot = cv2.bitwise_and(mat_region, cv2.bitwise_not(mat_color))
    pot = cv2.morphologyEx(pot, cv2.MORPH_OPEN, k, iterations=2)
    dk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (POT_DILATE, POT_DILATE))
    pot = cv2.dilate(pot, dk, iterations=1)
    cv2.imwrite(POT_MASK, pot)

    # 固定計測範囲 = マット範囲 − 鉢
    region = cv2.bitwise_and(mat_region, cv2.bitwise_not(pot))

    # 鉢周辺だけに絞る場合（FOCUS_BAND_PX>0）: 鉢の縁から帯状に切り出す
    if FOCUS_BAND_PX > 0:
        bk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * FOCUS_BAND_PX + 1, 2 * FOCUS_BAND_PX + 1))
        pot_band = cv2.dilate(pot, bk, iterations=1)
        region = cv2.bitwise_and(region, pot_band)

    cv2.imwrite(REGION_MASK, region)

    mat_area = int(cv2.countNonZero(mat_region))
    region_area = int(cv2.countNonZero(region))
    print(f"マット色を学習: 最頻色相H={peak}  下限={lower} 上限={upper}")
    print(f"固定計測範囲: {region_area}px / マット全体: {mat_area}px"
          + (f"（鉢周辺{FOCUS_BAND_PX}pxに限定）" if FOCUS_BAND_PX > 0 else "（鉢を除いた全体）"))
    print("annotated画像で 青線=計測範囲・黄線=除外(鉢) が意図どおりか確認してください。")
    print("ズレる場合はH/S/V_MARGIN、POT_DILATE、FOCUS_BAND_PXを調整して再実行してください。")


def run_once():
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    os.makedirs(ANNOTATED_DIR, exist_ok=True)
    lower, upper = load_mat_config()
    if not os.path.exists(REGION_MASK):
        sys.exit("計測範囲が未設定です。まず `--calibrate` を実行してください。")
    region = cv2.imread(REGION_MASK, cv2.IMREAD_GRAYSCALE)
    pot = cv2.imread(POT_MASK, cv2.IMREAD_GRAYSCALE) if os.path.exists(POT_MASK) else None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cap_path = os.path.join(CAPTURE_DIR, f"{ts}.jpg")
    capture_image(cap_path)
    img = cv2.imread(cap_path)
    if img is None:
        sys.exit("画像の読み込みに失敗しました。")

    coverage, clumps, annotated = analyze(img, lower, upper, region, pot)
    ann_path = os.path.join(ANNOTATED_DIR, f"{ts}.jpg")
    cv2.imwrite(ann_path, annotated)
    append_log(ts, coverage, clumps)

    print(f"[{ts}] 被覆面積率={coverage:.2f}%  塊数={clumps}  -> {ann_path}")
    return coverage


def main():
    parser = argparse.ArgumentParser(description="ミニトマト落ち葉モニタリング（鉢周辺・固定範囲）")
    parser.add_argument("--calibrate", action="store_true",
                        help="鉢を置いたまま落ち葉無しを撮影し、色学習＋固定計測範囲を作る")
    parser.add_argument("--loop", type=int, metavar="SEC",
                        help="指定秒ごとに繰り返し計測（cronを使わない場合）")
    args = parser.parse_args()

    if args.calibrate:
        calibrate()
        return

    if args.loop:
        print(f"{args.loop}秒ごとに計測します。Ctrl+Cで停止。")
        try:
            while True:
                run_once()
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\n停止しました。")
    else:
        run_once()


if __name__ == "__main__":
    main()
