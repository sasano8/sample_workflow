# 映像ストリームプロトコル
# WebRTC、RTSP、RTMP、HLS

# エッジコンピューティング
# GStreamer, FFmpeg, NVIDIA Jetson

# ストリームの配信
# Nginx-RTMP, WebRTC SFU, Kurento, Janus

"""
1. デバイスが FPS を送信するかどうか確認
2. FPS の動的推定を組み込む
3. 動画保存時に FPS を適用する実装を確定
"""


import cv2
import itertools
import time

class StreamAbortError(Exception):
    """ストリーム中断時に発せられる例外"""
    ...


def dummy_frame_generator(format=".jpg"):
    """ダミーのフレームデータ（JPEG）を送信する"""
    cap = cv2.VideoCapture(0)
    for _ in itertools.count():  # 無限ループ
        ret, frame = cap.read()
        if not ret:
            break

        success, buffer = cv2.imencode(format, frame)
        if not success:
            raise ValueError("Failed to encode frame to binary.")
        yield buffer.tobytes()
    cap.release()



def get_initial_fps(frame_iterator, num_samples=10):
    """
    サンプルからFPSを推定する

    :param frame_iterator: フレームデータのイテレータ
    :param num_samples: FPSを計算するためのフレーム数（デフォルト: 10）
    :return: フレームイテレータ, 計測されたFPS, is_static（デバイスが提供した fps なら True）
    """
    timestamps = []
    fps = None
    is_static = False

    for frame_data in frame_iterator:
        # フレームが FPS を提供している場合、それを優先する
        if isinstance(frame_data, tuple) and len(frame_data) == 2:
            frame, device_fps = frame_data
            if device_fps is not None:
                is_static = True
                return frame_iterator, device_fps, is_static
        else:
            frame = frame_data  # フレームのみのデータ

        timestamps.append(time.time())

        if len(timestamps) >= num_samples:
            fps = num_samples / (timestamps[-1] - timestamps[0])
            is_static = False
            return frame_iterator, fps, is_static



def estimate_fps(frame_iterator):
    """フレームの受信間隔を記録し、FPS を動的に推定する。"""
    timestamps = []
    for frame in frame_iterator:
        timestamps.append(time.time())
        if len(timestamps) > 10:  # 直近10フレームで計算
            fps = len(timestamps) / (timestamps[-1] - timestamps[0])
            timestamps.pop(0)  # 古いデータを削除
        else:
            fps = None  # 初期状態
        yield frame, fps


def frame_to_binary(frame_iterator, format=".jpg"):
    for frame, fps in frame_iterator:
        success, buffer = cv2.imencode(format, frame)
        if not success:
            raise ValueError("Failed to encode frame to binary.")
        yield buffer.tobytes(), fps


import time
import os
from itertools import islice

def to_batch_from_iterator(frame_iterator, fps=None):
    """
    """

    static_fps = fps

    if static_fps:
        for i, frame, _fps in enumerate(frame_iterator):
            batch = [(frame, _fps)] + list(islice(frame_iterator, static_fps))
            return i, batch
    else:
        for i, frame, dynamic_fps in enumerate(frame_iterator):
            batch = [(frame, dynamic_fps)] + list(islice(frame_iterator, dynamic_fps))
            return i, batch



frame_iterator, fps, is_static = get_initial_fps(dummy_frame_generator())

# 指定した fps または 動的に推定された fps のサイズのバッチを生成する
if is_static:
    # デバイスから送信された fps を固定で使う
    to_batch_from_iterator(frame_to_binary(frame_iterator), fps)
else:
    if "realtime_stimate":
        # 動的に fps を推定する
        frame_iterator = estimate_fps(frame_iterator)
        to_batch_from_iterator(frame_to_binary(frame_iterator), None)
    else:
        # 推定された fps を固定で使う
        to_batch_from_iterator(frame_to_binary(frame_iterator), fps)

# 課題
# デバイスから送信されるフレームが飛んでしまったりした場合、どのように保管し、保存される fps の単位を維持するか
# ネットワークの都合でフレームの順序が前後することがあるか
 