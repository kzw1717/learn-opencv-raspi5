#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
leaf_monitor.py 【学習用・注釈版】
ミニトマトの落ち葉モニタリング (Raspberry Pi 5 + Camera Module v1.3 / OV5647)

────────────────────────────────────────────────────────────
この注釈版について
  本ファイルは「raspi5-opencv入門テキスト」の学習用に、もとの
  leaf_monitor.py へ「どこで何を学んだか」を示すコメントを足した
  ものです。コードの動作はオリジナルと同一です。

  コメントの読み方（テキストの各ファイルに対応）:
    # 【第N章】... → 本編（第0章〜第10章）の対応する章
    # 【Bxx】...    → 用語解説 B01〜B09 の対応する解説
    # 【付録A】...  → 付録A「Python の構文・型・ライブラリ一覧」
                     （配列＝A.4 / オブジェクト＝A.5）
    # 【付録E】...  → 付録E「OpenCV のための NumPy 入門」
  これらの印を頼りに、テキストを行き来しながら読んでください。

  対応するテキスト一式:
    raspi5-opencv入門テキスト.md（本編・通し読み）
    A_Python構文と型とライブラリ.md / E_OpenCVのためのNumpy入門.md
    B01〜B09（用語解説） / C・D（付録）
────────────────────────────────────────────────────────────

用途: 鉢周辺の落ち葉の「増加トレンド」を被覆面積率で監視
手法: 色付きマットのHSV色抽出。鉢などの固定物は除外し、計測範囲は
      キャリブレーション時に固定 → 分母が一定なので日々の比較が正しくできる。
指標: 被覆面積率(%) = 落ち葉面積 / 固定有効マット面積 × 100

使い方:
  1) python3 leaf_monitor.py --calibrate   # 鉢あり・落ち葉なしで色と範囲を学習
  2) python3 leaf_monitor.py               # 1回計測
  3) python3 leaf_monitor.py --loop 3600   # 1時間ごとに計測
"""

# 【第6章 / B06: import文】必要な道具を最初に借りてくる。
#   標準ライブラリ（os/csv/json など）はインストール不要、
#   cv2・numpy は外部ライブラリ（apt で導入）。
import argparse              # 【B06】コマンドライン引数の解釈
import csv                   # 【B08: ファイルオブジェクト】CSVログの書き込み
import json                  # 【B02: 辞書型】設定を辞書↔JSONでやりとり
import os
import sys
import time
from datetime import datetime   # 【B06】datetimeの中のdatetimeだけ借りる書き方

import cv2                   # 【第1〜8章】画像処理の主役（OpenCV）
import numpy as np           # 【B09 / 付録E: NumPy】画像＝数字の表を扱う。慣習で np と略す

# ===================== 設定（環境に合わせて調整） =====================
# 【付録A.5: オブジェクト/モジュール】os.path.* はファイルの場所を組み立てる道具。
#   BASE_DIR はこのファイルの場所から自動で決まるので、作業フォルダ
#   （学習では ~/opencv_lesson、本番では leaf_monitor.py を置いた場所）に
#   依存せず動く。
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
MAT_CONFIG    = os.path.join(BASE_DIR, "mat_config.json")
REGION_MASK   = os.path.join(BASE_DIR, "region.png")   # 固定の計測範囲
POT_MASK      = os.path.join(BASE_DIR, "pot.png")       # 除外領域(表示用)
CAPTURE_DIR   = os.path.join(BASE_DIR, "captures")
ANNOTATED_DIR = os.path.join(BASE_DIR, "annotated")
LOG_CSV       = os.path.join(BASE_DIR, "log.csv")

RESOLUTION = (2028, 1520)   # 【付録A.3/A.4: タプル】変えない組はタプル()で持つ
SETTLE_SEC = 2.0            # 【付録A.3: float】小数

# --- 【第2章/第3章】マット色を見分けるHSV許容マージン ---
#   H（色相）を主役に、S・Vは照明変化に追従できるよう広め。第3章の「やってみよう」で動かした値。
H_MARGIN = 12      # 色相 ±（OpenCVのHは0-180）。マット判定の主役なので狭め
S_MARGIN = 70      # 彩度 ±。照明変化に追従できるよう広め
V_MARGIN = 80      # 明度 ±。影でも拾えるよう広め

# --- キャリブレーション時に「色付きのマット画素」とみなす条件 ---
SAT_MIN = 50       # 【第2章】これ未満の彩度は灰色っぽいので主色推定から除外
VAL_MIN = 40       # 暗すぎる画素を除外
VAL_MAX = 245      # 白飛びした画素を除外

# --- 領域・検出パラメータ ---
MORPH_KERNEL     = 5      # 【第4章】モルフォロジーのブラシ(カーネル)サイズ
MIN_MAT_FRAGMENT = 2000   # 【第6章】マット断片として採用する最小面積(px)
MIN_LEAF_AREA    = 600    # 【第6章】これ未満の塊は影・ノイズとして塊数から除外(px)
POT_DILATE       = 9      # 【第4章: dilate】鉢マスクを太らせて縁の取りこぼしを防ぐ

# --- 鉢周辺に絞る設定 ---
FOCUS_BAND_PX = 0   # 【第6章】0なら鉢を除いたマット全体。正の値で鉢の縁から帯状に限定
# =====================================================================


def capture_image(path):
    """picamera2で1枚撮影してJPEG保存（色順の罠を避けるためファイル経由）。"""
    # 【B04: try-except】カメラ用ライブラリが無い環境でも親切に終われるよう保険をかける。
    try:
        from picamera2 import Picamera2   # 【B06】必要な時に中の一部だけ借りる
    except ImportError:
        sys.exit("picamera2 が見つかりません。"
                 "`sudo apt install -y python3-picamera2 --no-install-recommends` を実行してください。")

    # 【B07 / 付録A.5: オブジェクト】カメラの実体を作り、メソッドで動作を命じる典型例。
    #   付録E eo2.py の自作クラス（PotImage）と同じ「もの→動作」の構図。
    picam2 = Picamera2()                                 # インスタンス化（実体を作る）
    config = picam2.create_still_configuration(main={"size": RESOLUTION})  # メソッド
    picam2.configure(config)                             # 設定を適用
    picam2.start()                                       # 起動
    time.sleep(SETTLE_SEC)                               # 露出・WBが安定するまで待つ
    picam2.capture_file(path)                            # 撮影してJPEG保存
    picam2.stop()                                        # 停止
    picam2.close()                                       # 後始末
    # 【第1章: BGRの罠】ここで一度JPEGに保存し、後でOpenCVが読み込む。
    #   こうすると色順の取り違え事故を避けられる。
    return path


def load_mat_config():
    """保存済みのマット色設定（HSV下限・上限）を読み込む。"""
    if not os.path.exists(MAT_CONFIG):   # 【第1章: if文】ファイルの有無で分岐
        sys.exit("マット色が未設定です。まず `--calibrate` を実行してください。")
    # 【B03: with】開いたら自動で閉じる。【B08】f はファイルオブジェクト。
    with open(MAT_CONFIG) as f:
        cfg = json.load(f)               # 【B02: 辞書型】JSON→辞書として読む
    # 【B02】辞書から "lower"/"upper" を名前で取り出し、
    #   【付録E E.8 / B09】np.array でリスト→NumPy配列にして返す。
    return np.array(cfg["lower"]), np.array(cfg["upper"])


def get_mat_mask(hsv, lower, upper):
    """マット色のマスク。色相が0/180をまたぐ場合（赤系）にも対応。"""
    # 【第3章】赤はH円の0と180をまたぐので、2範囲に分けて抽出し合体（| でOR）。
    #   青・緑マットなら下の最後の1行（単一範囲）だけで済む。
    if lower[0] < 0:
        lo1 = np.array([0, lower[1], lower[2]]);             up1 = np.array([upper[0], upper[1], upper[2]])
        lo2 = np.array([180 + lower[0], lower[1], lower[2]]); up2 = np.array([180, upper[1], upper[2]])
        return cv2.inRange(hsv, lo1, up1) | cv2.inRange(hsv, lo2, up2)
    if upper[0] > 180:
        lo1 = np.array([lower[0], lower[1], lower[2]]);      up1 = np.array([180, upper[1], upper[2]])
        lo2 = np.array([0, lower[1], lower[2]]);             up2 = np.array([upper[0] - 180, upper[1], upper[2]])
        return cv2.inRange(hsv, lo1, up1) | cv2.inRange(hsv, lo2, up2)
    # 【第3章: inRange】指定したHSV範囲の画素を白(255)に。これがマスク作りの核心。
    #   【付録E E.8】.astype(np.uint8) は型をそろえる（uint8）NumPyのメソッド。
    return cv2.inRange(hsv, lower.astype(np.uint8), upper.astype(np.uint8))


def mat_region_from_mask(mat_color):
    """マット色マスクからマットの外形（断片をまとめた凸包）を塗りつぶして返す。"""
    # 【第6章: findContours】白い領域のふちどり（輪郭）を取り出す。
    cnts, _ = cv2.findContours(mat_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 【第6章/B01: リスト内包表記】面積が十分大きい断片だけ集める（小さなゴミは無視）。
    pts = [c for c in cnts if cv2.contourArea(c) >= MIN_MAT_FRAGMENT]
    if not pts:
        if not cnts:
            return None
        pts = [max(cnts, key=cv2.contourArea)]
    # 【第6章: convexHull】断片を輪ゴムで囲って1つの外形に。
    #   【付録E E.8】np.vstack で複数断片の点を縦に積み重ねて1つにまとめる。
    hull = cv2.convexHull(np.vstack(pts))
    # 【第6章: fillPoly】【付録E E.6/E.8】np.zeros で真っ黒な台紙を作り、内部を白く塗ってマスク化。
    region = np.zeros(mat_color.shape, dtype=np.uint8)
    cv2.fillPoly(region, [hull], 255)
    return region


def analyze(img_bgr, lower, upper, region, pot):
    """固定計測範囲 region の中で、マット色でない部分＝落ち葉として被覆率を出す。"""
    # 【第2章: cvtColor】まず色味で判断できるようHSVに変換。
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mat_color = get_mat_mask(hsv, lower, upper)   # 【第3章】マット色マスク
    # 【第4章】ブラシを作り、オープニングで小さなノイズを消す。
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL, MORPH_KERNEL))
    mat_color = cv2.morphologyEx(mat_color, cv2.MORPH_OPEN, k, iterations=1)

    # 【第5章: ビット演算】「範囲の中(region)」かつ「マット色でない(not mat)」＝落ち葉。
    leaf_mask = cv2.bitwise_and(region, cv2.bitwise_not(mat_color))
    # 【第4章】落ち葉マスクも掃除：オープニングでノイズ消し→クロージングで穴埋め。
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, k, iterations=1)
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, k, iterations=2)

    # 【第7章: countNonZero】白い画素を数える＝面積。分母(region)は固定なので毎回同じ。
    #   （付録E E.6 の np.count_nonzero と働きは同じ。こちらは OpenCV 版。）
    region_area = int(cv2.countNonZero(region))   # ★ 固定なので毎回同じ
    leaf_area   = int(cv2.countNonZero(leaf_mask))
    # 【第7章/B04の考え方】0割りを避けるため条件式で守る。
    coverage_pct = 100.0 * leaf_area / region_area if region_area else 0.0

    # 【第6章】塊を数える：輪郭を取り、面積がMIN_LEAF_AREA以上のものだけ（B01: 内包表記）。
    leaf_cnts, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    clumps = [c for c in leaf_cnts if cv2.contourArea(c) >= MIN_LEAF_AREA]

    # 【第8章: 可視化】もとを壊さないようコピーに、青=範囲・黄=鉢・緑=堆積物を描く。
    annotated = img_bgr.copy()                    # 【B07 / 付録A.5】copyはメソッド
    rcnts, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(annotated, rcnts, -1, (255, 0, 0), 2)   # 計測範囲: 青（BGRで青）
    if pot is not None:                           # 【第1章: if/None】鉢マスクがあれば描く
        pcnts, _ = cv2.findContours(pot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(annotated, pcnts, -1, (0, 255, 255), 2)  # 除外(鉢): 黄
    cv2.drawContours(annotated, clumps, -1, (0, 255, 0), 2)  # 落ち葉: 緑
    # 【第8章: putText】数値を画像に書き込む。色(0,0,255)はBGRなので赤。
    label = f"coverage={coverage_pct:.2f}%  clumps={len(clumps)}"   # 【付録A.2】f文字列
    cv2.putText(annotated, label, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    return coverage_pct, len(clumps), annotated   # 【付録A.3: タプル】3つまとめて返す


def append_log(timestamp, coverage, clumps):
    """計測結果を log.csv に1行追記する。"""
    new_file = not os.path.exists(LOG_CSV)        # 【付録A.3: bool】新規ファイルか
    # 【B03: with】+【B08: ファイルオブジェクト】"a"=追記モードで開く。
    #   付録E eo3.py で体験したCSV追記とまったく同じ形。
    with open(LOG_CSV, "a", newline="") as f:
        w = csv.writer(f)                          # 【B08】ファイルオブジェクトをcsvに渡す
        if new_file:
            w.writerow(["timestamp", "coverage_pct", "clumps"])   # 初回だけ見出し行
        w.writerow([timestamp, f"{coverage:.3f}", clumps])        # 1回分のデータ行


def calibrate():
    """鉢を置いたまま落ち葉無しの状態を撮影し、マット色学習＋固定計測範囲を作る。"""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    print("マット上に鉢・支柱は通常どおり置き、落ち葉が無い状態で撮影します...")
    path = os.path.join(CAPTURE_DIR, "_calib.jpg")
    capture_image(path)
    img = cv2.imread(path)                         # 【第1章: imread】画像＝数字の表
    if img is None:
        sys.exit("撮影画像の読み込みに失敗しました。")

    # 【第2章: cvtColor】HSVへ。【付録A.4 / 付録E E.4】スライスでH/S/Vの3チャンネルに分ける。
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    Hc, Sc, Vc = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # 【付録E E.5/E.6: NumPy】真偽配列で「有彩色の画素」を一括選別（forで1画素ずつ回さない）。
    #   ＝付録E e5.py の①。Sc/Vc を比較すると True/False の配列ができる。
    valid = (Sc > SAT_MIN) & (Vc > VAL_MIN) & (Vc < VAL_MAX)
    if np.count_nonzero(valid) < 1000:             # 【付録E E.6】Trueの数を数える
        sys.exit("色付き画素が少なすぎます。マットがフレームに大きく写るようにしてください。")
    # 【付録E E.7】色相ヒストグラム(bincount)の最頻値(argmax)＝最大面積の色＝マット色。
    peak = int(np.argmax(np.bincount(Hc[valid].ravel(), minlength=180)))

    # 【付録E E.7】最頻色相の近くの画素から、彩度・明度の代表値(median=中央値)を取る。
    #   np.abs / np.minimum は色相の「距離」計算（H は円状なので近いほうを取る）。
    hue_dist = np.minimum(np.abs(Hc.astype(int) - peak), 180 - np.abs(Hc.astype(int) - peak))
    matpix = valid & (hue_dist <= H_MARGIN)
    s_med, v_med = int(np.median(Sc[matpix])), int(np.median(Vc[matpix]))

    # 【第3章】「代表色 ± マージン」でHSVの下限・上限を作る（テキスト step10 と同じ考え方）。
    lower = [peak - H_MARGIN, max(0, s_med - S_MARGIN), max(0, v_med - V_MARGIN)]
    upper = [peak + H_MARGIN, min(255, s_med + S_MARGIN), min(255, v_med + V_MARGIN)]
    # 【B02: 辞書型】+【B03: with】設定を辞書にしてJSON保存。
    with open(MAT_CONFIG, "w") as f:
        json.dump({"lower": lower, "upper": upper, "peak_hue": peak}, f, indent=2)

    # 【第3章】学習した範囲でマット色マスクを作り、【第4章】オープニングで掃除。
    mat_color = get_mat_mask(hsv, np.array(lower), np.array(upper))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPH_KERNEL, MORPH_KERNEL))
    mat_color = cv2.morphologyEx(mat_color, cv2.MORPH_OPEN, k, iterations=1)
    # 【第6章】断片を凸包で1つのマット外形にまとめる。
    mat_region = mat_region_from_mask(mat_color)
    if mat_region is None:
        sys.exit("マットが検出できませんでした。色や照明を確認してください。")

    # 【第5章: ビット演算】落ち葉が無いので「マット範囲 かつ マット色でない」＝鉢など固定物。
    pot = cv2.bitwise_and(mat_region, cv2.bitwise_not(mat_color))
    pot = cv2.morphologyEx(pot, cv2.MORPH_OPEN, k, iterations=2)   # 【第4章】掃除
    # 【第4章: dilate】鉢を少し太らせて縁の取りこぼしを防ぐ。
    dk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (POT_DILATE, POT_DILATE))
    pot = cv2.dilate(pot, dk, iterations=1)
    cv2.imwrite(POT_MASK, pot)                     # 【第1章: imwrite】確認用に保存

    # 【第5章/第7章】固定計測範囲 = マット範囲 − 鉢。これが不変の「ものさし」になる。
    region = cv2.bitwise_and(mat_region, cv2.bitwise_not(pot))

    # 【第6章】鉢周辺だけに絞る場合：鉢の縁から帯状(dilate)に切り出して交差をとる。
    if FOCUS_BAND_PX > 0:
        bk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * FOCUS_BAND_PX + 1, 2 * FOCUS_BAND_PX + 1))
        pot_band = cv2.dilate(pot, bk, iterations=1)
        region = cv2.bitwise_and(region, pot_band)

    cv2.imwrite(REGION_MASK, region)               # 【第7章】計測範囲を固定保存（region.png）

    mat_area = int(cv2.countNonZero(mat_region))   # 【第7章】面積を数えて表示
    region_area = int(cv2.countNonZero(region))
    print(f"マット色を学習: 最頻色相H={peak}  下限={lower} 上限={upper}")
    print(f"固定計測範囲: {region_area}px / マット全体: {mat_area}px"
          + (f"（鉢周辺{FOCUS_BAND_PX}pxに限定）" if FOCUS_BAND_PX > 0 else "（鉢を除いた全体）"))
    print("annotated画像で 青線=計測範囲・黄線=除外(鉢) が意図どおりか確認してください。")
    print("ズレる場合はH/S/V_MARGIN、POT_DILATE、FOCUS_BAND_PXを調整して再実行してください。")


def run_once():
    """1回分の計測（撮影→解析→記録）を行う。"""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    os.makedirs(ANNOTATED_DIR, exist_ok=True)
    lower, upper = load_mat_config()               # 【B02】保存した色設定を読む
    if not os.path.exists(REGION_MASK):
        sys.exit("計測範囲が未設定です。まず `--calibrate` を実行してください。")
    # 【第7章】固定の計測範囲・鉢マスクを「白黒で」読み戻す（毎回同じものさし）。
    region = cv2.imread(REGION_MASK, cv2.IMREAD_GRAYSCALE)
    pot = cv2.imread(POT_MASK, cv2.IMREAD_GRAYSCALE) if os.path.exists(POT_MASK) else None

    # 【B06】datetimeで撮影時刻の文字列を作り、ファイル名に使う。
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cap_path = os.path.join(CAPTURE_DIR, f"{ts}.jpg")
    capture_image(cap_path)
    img = cv2.imread(cap_path)                      # 【第1章: imread】
    if img is None:
        sys.exit("画像の読み込みに失敗しました。")

    # 【第2〜8章】解析の本体（cvtColor→inRange→morphology→bitwise→countNonZero→描画）。
    coverage, clumps, annotated = analyze(img, lower, upper, region, pot)
    ann_path = os.path.join(ANNOTATED_DIR, f"{ts}.jpg")
    cv2.imwrite(ann_path, annotated)               # 【第1章/第8章】確認画像を保存
    append_log(ts, coverage, clumps)               # 【B08】CSVに追記

    print(f"[{ts}] 被覆面積率={coverage:.2f}%  塊数={clumps}  -> {ann_path}")
    return coverage


def main():
    """コマンドライン引数を読み取り、適切な処理に振り分ける入口。"""
    # 【B06/B07】argparseのオブジェクトを作り、メソッドで引数を定義・解釈する。
    parser = argparse.ArgumentParser(description="ミニトマト落ち葉モニタリング（鉢周辺・固定範囲）")
    parser.add_argument("--calibrate", action="store_true",
                        help="鉢を置いたまま落ち葉無しを撮影し、色学習＋固定計測範囲を作る")
    parser.add_argument("--loop", type=int, metavar="SEC",
                        help="指定秒ごとに繰り返し計測（cronを使わない場合）")
    args = parser.parse_args()                      # 【B07】argsオブジェクトに結果が入る

    if args.calibrate:                              # 【B07: 属性アクセス】+ if文
        calibrate()
        return

    if args.loop:
        print(f"{args.loop}秒ごとに計測します。Ctrl+Cで停止。")
        # 【B04: try-except】無限ループ(while True)をCtrl+Cできれいに止める。
        try:
            while True:                             # 【while文】条件が真の間くりかえす
                run_once()
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\n停止しました。")
    else:
        run_once()


# 【B05: if __name__ == "__main__"】直接実行したときだけ main() を呼ぶ。
#   import されたときは（関数だけ借りられ）ここは動かない。
if __name__ == "__main__":
    main()
